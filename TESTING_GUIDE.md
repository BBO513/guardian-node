# Guardian Node Testing Guide
## Post-Fix Verification

This guide will help you test the Guardian Node application after the LLM integration fixes.

## Prerequisites

- Docker and Docker Compose installed
- At least 4GB of free RAM
- Model file: `models/gemma-2-2b-it-Q4_K_M.gguf` (1.6GB)

## Quick Test (Local Python)

Before building Docker, verify the fixes work locally:

```bash
cd guardian_node_clean
python test_llm_fix.py
```

Expected output:
```
✓ Successfully imported llm_integration
✓ Configuration loaded
✓ Model file found: models/gemma-2-2b-it-Q4_K_M.gguf
✓ LLM object created: GuardianLLM
✓ Model type correctly set to 'gemma'
✓ main.py has no syntax errors
All tests passed! ✓
```

## Docker Build and Run

### Option 1: Using the Script (Recommended)

**Linux/Mac:**
```bash
chmod +x rebuild_and_run.sh
./rebuild_and_run.sh
```

**Windows:**
```cmd
rebuild_and_run.bat
```

### Option 2: Manual Commands

```bash
# Stop existing containers
docker-compose down

# Rebuild (no cache to ensure fresh build)
docker-compose build --no-cache

# Run the container
docker-compose up
```

## Testing the Application

Once the container is running, you should see:

```
🛡️ Starting Guardian Node...
💻 Running in CLI mode...
Guardian Family Assistant CLI. Type 'help' for commands.
guardian-family>
```

### Test Commands

1. **Show Help**
   ```
   guardian-family> help
   ```
   Expected: Display of all available commands

2. **List Family Skills**
   ```
   guardian-family> family skills
   ```
   Expected: List of registered family cybersecurity skills

3. **Ask a Question (Main Test)**
   ```
   guardian-family> ask How can I keep my child safe online?
   ```
   Expected: 
   - No IndentationError
   - No AttributeError about missing functions
   - LLM generates a family-friendly response
   - Response includes safety recommendations

4. **Test Threat Analysis**
   ```
   guardian-family> family skill threat_analysis
   ```
   Expected: Skill executes successfully

5. **Analyze Family Security**
   ```
   guardian-family> family analyze
   ```
   Expected: Security analysis results

6. **Get Recommendations**
   ```
   guardian-family> family recommendations
   ```
   Expected: List of security recommendations

7. **Check Status**
   ```
   guardian-family> family status
   ```
   Expected: "Family Assistant is running. All systems nominal."

## Expected Behavior

### ✅ Success Indicators

1. **Container Starts Successfully**
   - No Python syntax errors
   - No IndentationError
   - No AttributeError about missing functions

2. **Model Loads**
   - Log shows: "Loading LLM model: .../gemma-2-2b-it-Q4_K_M.gguf (Type: gemma)"
   - Log shows: "LLM model loaded successfully"

3. **Ask Command Works**
   - Processes user query
   - Generates LLM-enhanced response
   - Shows confidence score
   - Suggests follow-up questions

4. **Gemma-Specific Formatting**
   - Uses `<start_of_turn>` prompt format
   - Generates coherent responses
   - No model type mismatch errors

### ❌ Failure Indicators

If you see these errors, something went wrong:

1. **IndentationError: unexpected indent**
   - Issue: main.py line ~356 not fixed properly
   - Solution: Check `_enhance_response_with_llm()` method

2. **AttributeError: 'GuardianLLM' object has no attribute 'load_model'**
   - Issue: Old function call still present
   - Solution: Check main.py line ~31

3. **Model file not found**
   - Issue: Model not in correct location
   - Solution: Ensure `models/gemma-2-2b-it-Q4_K_M.gguf` exists

4. **Type: phi3 in logs**
   - Issue: Model type not updated
   - Solution: Check app_config_canonical.yaml and llm_integration.py

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs guardian-node

# Check if model file is accessible
docker-compose run guardian-node ls -lh /app/models/
```

### Model Not Loading

```bash
# Verify model file in container
docker-compose run guardian-node ls -lh /app/models/gemma-2-2b-it-Q4_K_M.gguf

# Check configuration
docker-compose run guardian-node cat /app/guardian_interpreter/app_config_canonical.yaml
```

### Out of Memory

If the container crashes with OOM:

1. Increase Docker memory limit (Docker Desktop settings)
2. Reduce context_length in config (from 4096 to 2048)
3. Use fewer CPU threads (from 4 to 2)

### Slow Response Times

Normal for first query (model loading):
- First query: 10-30 seconds
- Subsequent queries: 2-5 seconds

If consistently slow:
- Check CPU usage
- Reduce max_tokens (from 512 to 256)
- Increase threads if CPU has more cores

## Performance Benchmarks

Expected performance on different systems:

**Raspberry Pi 4 (4GB RAM):**
- Model load time: 30-60 seconds
- First query: 20-40 seconds
- Subsequent queries: 5-10 seconds

**Desktop (8GB+ RAM, 4+ cores):**
- Model load time: 10-20 seconds
- First query: 5-15 seconds
- Subsequent queries: 2-5 seconds

**High-end System (16GB+ RAM, 8+ cores):**
- Model load time: 5-10 seconds
- First query: 3-8 seconds
- Subsequent queries: 1-3 seconds

## Sample Test Session

```
guardian-family> help
[Shows help text]

guardian-family> family skills
Available Family Skills:
----------------------------------------
 1. family_cyber_skills      - Family cybersecurity skill
 2. threat_analysis_skill    - Family cybersecurity skill
 3. device_guidance_skill    - Family cybersecurity skill
 4. child_education_skill    - Family cybersecurity skill

guardian-family> ask How do I set up parental controls?

Family Assistant Response:
[LLM generates detailed, family-friendly response about parental controls]

Confidence: 0.85
✨ Enhanced with AI reasoning

Follow-up questions you might ask:
  1. What are the best parental control apps?
  2. How do I monitor my child's online activity?
  3. What age-appropriate content filters should I use?

guardian-family> exit
Exiting.
```

## Success Criteria

The fixes are successful if:

1. ✅ Container builds without errors
2. ✅ Application starts without IndentationError
3. ✅ Model loads with "Type: gemma" in logs
4. ✅ `ask` command generates responses
5. ✅ No AttributeError about missing functions
6. ✅ Family skills execute successfully
7. ✅ Responses are coherent and family-friendly

## Next Steps After Successful Testing

1. **Production Deployment**
   - Run in detached mode: `docker-compose up -d`
   - Set up automatic restart: Already configured with `restart: unless-stopped`

2. **Monitoring**
   - Enable monitoring profile: `docker-compose --profile monitoring up -d`
   - Access Prometheus: http://localhost:9090

3. **Customization**
   - Adjust model parameters in `app_config_canonical.yaml`
   - Add custom family skills in `guardian_interpreter/skills/`
   - Configure family profiles in `data/families/`

4. **GUI Mode** (if needed)
   - Run with GUI: `docker-compose run guardian-node python guardian_interpreter/main.py --gui`
   - Access GUI: http://localhost:8080

## Support

If issues persist after following this guide:

1. Check `FIXES_APPLIED.md` for detailed fix information
2. Review logs: `docker-compose logs -f guardian-node`
3. Verify all files were modified correctly
4. Ensure model file is not corrupted (check file size: ~1.6GB)
