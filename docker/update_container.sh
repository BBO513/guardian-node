#!/bin/bash
set -e

# Guardian Node Container Update Script
# Handles safe updates of the Guardian Node container

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
COMPOSE_FILE="$PROJECT_DIR/docker-compose.yml"
BACKUP_DIR="$PROJECT_DIR/backups"
LOG_FILE="$PROJECT_DIR/logs/update.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

# Check if running as root
check_permissions() {
    if [[ $EUID -eq 0 ]]; then
        warning "Running as root. Consider using a non-root user with docker group membership."
    fi
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check if docker is installed
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed or not in PATH"
        exit 1
    fi
    
    # Check if docker-compose is installed
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed or not in PATH"
        exit 1
    fi
    
    # Check if compose file exists
    if [ ! -f "$COMPOSE_FILE" ]; then
        error "Docker Compose file not found: $COMPOSE_FILE"
        exit 1
    fi
    
    success "Prerequisites check passed"
}

# Create backup before update
create_backup() {
    log "Creating backup before update..."
    
    mkdir -p "$BACKUP_DIR"
    
    BACKUP_TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    BACKUP_NAME="guardian-backup-$BACKUP_TIMESTAMP"
    
    # Create backup directory
    mkdir -p "$BACKUP_DIR/$BACKUP_NAME"
    
    # Backup data directory
    if [ -d "$PROJECT_DIR/data" ]; then
        log "Backing up data directory..."
        cp -r "$PROJECT_DIR/data" "$BACKUP_DIR/$BACKUP_NAME/"
    fi
    
    # Backup configuration
    if [ -d "$PROJECT_DIR/config" ]; then
        log "Backing up configuration..."
        cp -r "$PROJECT_DIR/config" "$BACKUP_DIR/$BACKUP_NAME/"
    fi
    
    # Backup logs (recent only)
    if [ -d "$PROJECT_DIR/logs" ]; then
        log "Backing up recent logs..."
        mkdir -p "$BACKUP_DIR/$BACKUP_NAME/logs"
        find "$PROJECT_DIR/logs" -name "*.log" -mtime -7 -exec cp {} "$BACKUP_DIR/$BACKUP_NAME/logs/" \;
    fi
    
    # Create backup archive
    cd "$BACKUP_DIR"
    tar -czf "$BACKUP_NAME.tar.gz" "$BACKUP_NAME"
    rm -rf "$BACKUP_NAME"
    
    success "Backup created: $BACKUP_DIR/$BACKUP_NAME.tar.gz"
    
    # Keep only last 5 backups
    ls -t "$BACKUP_DIR"/guardian-backup-*.tar.gz | tail -n +6 | xargs -r rm --
}

# Check container health before update
check_current_health() {
    log "Checking current container health..."
    
    # Check if container is running
    if docker-compose -f "$COMPOSE_FILE" ps | grep -q "Up"; then
        log "Container is currently running"
        
        # Run health check
        if docker-compose -f "$COMPOSE_FILE" exec -T guardian-node python /app/health_check.py --comprehensive; then
            success "Current container is healthy"
            return 0
        else
            warning "Current container has health issues"
            return 1
        fi
    else
        warning "Container is not currently running"
        return 1
    fi
}

# Pull latest images
pull_images() {
    log "Pulling latest images..."
    
    if docker-compose -f "$COMPOSE_FILE" pull; then
        success "Images pulled successfully"
    else
        error "Failed to pull images"
        exit 1
    fi
}

# Stop services gracefully
stop_services() {
    log "Stopping Guardian Node services..."
    
    # Give services time to shut down gracefully
    if docker-compose -f "$COMPOSE_FILE" stop --timeout 30; then
        success "Services stopped gracefully"
    else
        warning "Services did not stop gracefully, forcing shutdown..."
        docker-compose -f "$COMPOSE_FILE" kill
    fi
}

# Start services
start_services() {
    log "Starting Guardian Node services..."
    
    if docker-compose -f "$COMPOSE_FILE" up -d; then
        success "Services started successfully"
    else
        error "Failed to start services"
        return 1
    fi
}

# Wait for services to be healthy
wait_for_health() {
    log "Waiting for services to become healthy..."
    
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        log "Health check attempt $attempt/$max_attempts..."
        
        # Wait a bit for services to start
        sleep 10
        
        # Check if container is running
        if docker-compose -f "$COMPOSE_FILE" ps | grep -q "Up"; then
            # Run health check
            if docker-compose -f "$COMPOSE_FILE" exec -T guardian-node python /app/health_check.py; then
                success "Services are healthy"
                return 0
            fi
        fi
        
        attempt=$((attempt + 1))
    done
    
    error "Services did not become healthy within expected time"
    return 1
}

# Rollback to previous version
rollback() {
    error "Update failed. Initiating rollback..."
    
    # Stop current services
    docker-compose -f "$COMPOSE_FILE" down
    
    # Find latest backup
    LATEST_BACKUP=$(ls -t "$BACKUP_DIR"/guardian-backup-*.tar.gz 2>/dev/null | head -n 1)
    
    if [ -n "$LATEST_BACKUP" ]; then
        log "Restoring from backup: $LATEST_BACKUP"
        
        # Extract backup
        cd "$BACKUP_DIR"
        tar -xzf "$(basename "$LATEST_BACKUP")"
        BACKUP_FOLDER=$(basename "$LATEST_BACKUP" .tar.gz)
        
        # Restore data
        if [ -d "$BACKUP_FOLDER/data" ]; then
            rm -rf "$PROJECT_DIR/data"
            cp -r "$BACKUP_FOLDER/data" "$PROJECT_DIR/"
        fi
        
        # Restore config
        if [ -d "$BACKUP_FOLDER/config" ]; then
            rm -rf "$PROJECT_DIR/config"
            cp -r "$BACKUP_FOLDER/config" "$PROJECT_DIR/"
        fi
        
        # Clean up extracted backup
        rm -rf "$BACKUP_FOLDER"
        
        # Start services with previous configuration
        start_services
        
        if wait_for_health; then
            success "Rollback completed successfully"
        else
            error "Rollback failed. Manual intervention required."
            exit 1
        fi
    else
        error "No backup found for rollback. Manual intervention required."
        exit 1
    fi
}

# Main update function
perform_update() {
    log "Starting Guardian Node update process..."
    
    # Create backup
    create_backup
    
    # Check current health (optional - continue even if unhealthy)
    check_current_health || warning "Proceeding with update despite health issues"
    
    # Pull latest images
    pull_images
    
    # Stop services
    stop_services
    
    # Start services with new images
    if start_services; then
        # Wait for services to become healthy
        if wait_for_health; then
            success "Update completed successfully!"
            
            # Show status
            log "Current service status:"
            docker-compose -f "$COMPOSE_FILE" ps
            
            # Run comprehensive health check
            log "Running post-update health check..."
            docker-compose -f "$COMPOSE_FILE" exec -T guardian-node python /app/health_check.py --comprehensive
            
        else
            error "Update failed - services are not healthy"
            rollback
            exit 1
        fi
    else
        error "Failed to start services after update"
        rollback
        exit 1
    fi
}

# Cleanup old images and containers
cleanup() {
    log "Cleaning up old Docker images and containers..."
    
    # Remove unused images
    docker image prune -f
    
    # Remove unused containers
    docker container prune -f
    
    # Remove unused volumes (be careful with this)
    # docker volume prune -f
    
    success "Cleanup completed"
}

# Show usage
show_usage() {
    echo "Guardian Node Container Update Script"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --help, -h          Show this help message"
    echo "  --backup-only       Create backup only, don't update"
    echo "  --no-backup         Skip backup creation"
    echo "  --cleanup           Cleanup old images after update"
    echo "  --force             Force update even if health checks fail"
    echo ""
    echo "Examples:"
    echo "  $0                  # Standard update with backup"
    echo "  $0 --cleanup        # Update and cleanup old images"
    echo "  $0 --backup-only    # Create backup only"
}

# Parse command line arguments
BACKUP_ONLY=false
NO_BACKUP=false
CLEANUP_AFTER=false
FORCE_UPDATE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --help|-h)
            show_usage
            exit 0
            ;;
        --backup-only)
            BACKUP_ONLY=true
            shift
            ;;
        --no-backup)
            NO_BACKUP=true
            shift
            ;;
        --cleanup)
            CLEANUP_AFTER=true
            shift
            ;;
        --force)
            FORCE_UPDATE=true
            shift
            ;;
        *)
            error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Main execution
main() {
    log "Guardian Node Update Script Started"
    log "Project Directory: $PROJECT_DIR"
    
    # Create logs directory
    mkdir -p "$(dirname "$LOG_FILE")"
    
    # Check permissions and prerequisites
    check_permissions
    check_prerequisites
    
    if [ "$BACKUP_ONLY" = true ]; then
        create_backup
        success "Backup completed. Exiting."
        exit 0
    fi
    
    # Create backup unless explicitly disabled
    if [ "$NO_BACKUP" != true ]; then
        create_backup
    fi
    
    # Perform the update
    perform_update
    
    # Cleanup if requested
    if [ "$CLEANUP_AFTER" = true ]; then
        cleanup
    fi
    
    success "Guardian Node update process completed successfully!"
    log "Update log saved to: $LOG_FILE"
}

# Run main function
main "$@"