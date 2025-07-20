# Guardian Node Family User Guide

**Your Personal AI Cybersecurity Assistant - Setup and Usage Guide**

---

## 🏠 Welcome to Guardian Node

Guardian Node is your family's personal cybersecurity assistant that runs completely offline in your home. It helps protect your family from online threats while keeping all your data private and secure.

---

## 🚀 Quick Setup Guide

### What You'll Need
- **Raspberry Pi 5** (16GB RAM recommended) OR any computer with 8GB+ RAM
- **Internet connection** (only for initial setup)
- **30 minutes** of your time

### Option 1: Easy Docker Setup (Recommended)

1. **Download Guardian Node**
   ```bash
   # On your computer or Raspberry Pi, open terminal and run:
   git clone https://github.com/your-org/guardian-node.git
   cd guardian-node
   ```

2. **Start Guardian Node**
   ```bash
   # This will download and start everything automatically
   docker-compose up -d
   ```

3. **Access Your Guardian Node**
   - Open your web browser
   - Go to: `http://localhost:8080` (or your device's IP address)
   - You should see the Guardian Node interface

### Option 2: Direct Installation

1. **Install Python** (if not already installed)
   ```bash
   # On Raspberry Pi or Linux:
   sudo apt update
   sudo apt install python3 python3-pip git
   
   # On Windows: Download Python from python.org
   # On Mac: brew install python3
   ```

2. **Download and Setup Guardian Node**
   ```bash
   git clone https://github.com/your-org/guardian-node.git
   cd guardian-node/guardian_interpreter
   pip3 install -r requirements.txt
   ```

3. **Start Guardian Node**
   ```bash
   python3 main.py
   ```

---

## 🛡️ Using Guardian Node

### Getting Started

When you first start Guardian Node, you'll see:
```
Guardian Interpreter v1.0.0
Owner: Guardian Team
Type 'help' for commands, 'quit' to exit
```

### Basic Commands

#### Get Help
```
Guardian> help
```
Shows all available commands and examples.

#### Ask Questions
```
Guardian> ask "How can I keep my child safe online?"
Guardian> ask "What are the signs of a phishing email?"
Guardian> ask "How do I secure my home WiFi?"
```

#### Check Your Security
```
Guardian> family analyze
```
Analyzes your family's cybersecurity posture and provides a security score.

#### Get Recommendations
```
Guardian> family recommendations
```
Provides personalized security recommendations for your family.

#### Run Security Tools
```
Guardian> family skills
Guardian> family skill password_check mypassword123
Guardian> family skill threat_analysis
```

---

## 👨‍👩‍👧‍👦 Family Features

### 1. **Child Safety Tools**
- **Parental Control Check**: Verify your parental control settings
- **Safe Browsing Education**: Teach kids about online safety
- **Age-Appropriate Responses**: All answers are family-friendly

### 2. **Password Security**
- **Password Strength Checker**: Test how strong your passwords are
- **Password Education**: Learn how to create strong passwords
- **Family Password Policy**: Get recommendations for your family

### 3. **Phishing Protection**
- **Email Safety**: Learn to identify suspicious emails
- **Link Checking**: Understand safe browsing practices
- **Scam Awareness**: Stay informed about current scams

### 4. **Network Security**
- **WiFi Security Check**: Ensure your home network is secure
- **Device Scanning**: Check all devices on your network
- **Router Security**: Verify your router settings

---

## 🔒 Privacy Features

### Your Data Stays Home
- **No Cloud**: Everything runs on your device
- **No Tracking**: We don't collect any personal information
- **No Internet Required**: Works completely offline after setup
- **Full Control**: You own and control all your data

### What Gets Logged
- **Security Events**: For your protection and audit
- **Usage Statistics**: To improve performance (stays local)
- **Error Logs**: To help troubleshoot issues

### What Doesn't Get Logged
- **Personal Information**: Never stored or transmitted
- **Browsing History**: We don't track your web activity
- **Private Conversations**: Family discussions stay private

---

## 📱 Daily Usage Examples

### Morning Security Check
```
Guardian> family analyze
Guardian> family recommendations
```

### Teaching Kids About Online Safety
```
Guardian> ask "How do I explain phishing to my 10-year-old?"
Guardian> family skill phishing_education
```

### Checking a Suspicious Email
```
Guardian> ask "I received an email asking for my bank details. Is this safe?"
```

### Setting Up New Device Security
```
Guardian> ask "I just bought a new tablet for my teenager. How do I secure it?"
Guardian> family skill device_scan
```

### Weekly Password Review
```
Guardian> family skill password_check
Guardian> ask "How often should I change my passwords?"
```

---

## 🔧 Customization

### Family Profile Setup
You can customize Guardian Node for your family:

1. **Family Size**: Configure for your number of family members
2. **Age Groups**: Set appropriate content for different ages
3. **Security Level**: Choose from basic, standard, or advanced
4. **Notification Preferences**: Set how you want to receive alerts

### Adding Family Members
```
Guardian> family profile add_member "Child" age:12 tech_level:beginner
```

### Setting Security Preferences
```
Guardian> family settings security_level:standard
Guardian> family settings child_safe_mode:true
```

---

## 🆘 Troubleshooting

### Guardian Node Won't Start
1. **Check if Python is installed**: `python3 --version`
2. **Check if all dependencies are installed**: `pip3 list`
3. **Look at error messages**: They usually tell you what's wrong
4. **Restart your device**: Sometimes this fixes connection issues

### Can't Access Web Interface
1. **Check the address**: Make sure you're using the right IP address
2. **Check firewall**: Your firewall might be blocking the connection
3. **Try different port**: Use `:8080` or `:8443` at the end of the address

### Commands Not Working
1. **Type 'help'**: See all available commands
2. **Check spelling**: Commands are case-sensitive
3. **Use quotes**: For questions with spaces, use quotes: `ask "my question"`

### Getting Strange Responses
1. **Be specific**: Ask clear, specific questions
2. **Use family mode**: Make sure family assistant is enabled
3. **Check logs**: Look in the logs folder for error messages

---

## 📞 Getting Help

### Built-in Help
```
Guardian> help                    # General help
Guardian> family help            # Family assistant help
Guardian> status                 # Check system status
```

### Log Files
If something isn't working, check these files:
- `logs/guardian.log` - Main application log
- `logs/family_audit.log` - Family assistant activities
- `logs/blocked_calls.log` - Blocked network requests

### Community Support
- **Documentation**: Check the full documentation in the `docs/` folder
- **GitHub Issues**: Report bugs or request features
- **Community Forum**: Connect with other Guardian Node families

---

## 🔄 Keeping Guardian Node Updated

### Automatic Updates (Docker)
```bash
# Update to latest version
cd guardian-node
docker-compose pull
docker-compose up -d
```

### Manual Updates
```bash
# Update the code
cd guardian-node
git pull origin main

# Update dependencies
pip3 install -r guardian_interpreter/requirements.txt --upgrade

# Restart Guardian Node
```

---

## 🎯 Best Practices for Families

### Daily Habits
- **Morning Check**: Quick security status review
- **Evening Review**: Check any security alerts
- **Weekly Analysis**: Run full family security analysis

### Teaching Kids
- **Make it Fun**: Use Guardian Node to teach cybersecurity as a game
- **Regular Discussions**: Talk about online safety weekly
- **Lead by Example**: Show kids how you use security tools

### Staying Secure
- **Keep Updated**: Update Guardian Node regularly
- **Monitor Logs**: Check security logs weekly
- **Follow Recommendations**: Act on security suggestions
- **Stay Informed**: Ask Guardian Node about new threats

---

## 🌟 Advanced Features

### Voice Interface (Coming Soon)
- **Wake Word**: "Hey Guardian"
- **Voice Commands**: Ask questions by speaking
- **Family-Friendly**: Safe for all ages

### Mobile App (Planned)
- **Remote Monitoring**: Check your home security from anywhere
- **Push Notifications**: Get alerts on your phone
- **Family Dashboard**: See everyone's security status

### Smart Home Integration (Future)
- **IoT Device Monitoring**: Check smart home device security
- **Network Monitoring**: Real-time network threat detection
- **Automated Responses**: Automatic threat mitigation

---

## 📋 Quick Reference Card

### Essential Commands
```bash
help                              # Show all commands
ask "question"                    # Ask cybersecurity questions
family analyze                    # Security analysis
family recommendations            # Get security advice
family skills                     # List security tools
family skill password_check pwd   # Check password strength
status                           # System status
quit                             # Exit Guardian Node
```

### Emergency Commands
```bash
family skill threat_analysis     # Check for immediate threats
family skill device_scan         # Scan all devices
family skill network_security_audit  # Check network security
```

---

**Remember: Guardian Node is designed to help your family stay safe online while keeping your privacy intact. Your data never leaves your home, and you're always in control.**

**Stay safe, stay private, stay protected with Guardian Node! 🛡️**