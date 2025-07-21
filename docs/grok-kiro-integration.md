<<<<<<< HEAD
# Grok + Kiro Integration Guide

**Connect Grok AI to Guardian Node via Kiro IDE**

This guide shows you how to safely connect Grok (xAI's AI assistant) to your Guardian Node family cybersecurity system through Kiro IDE using Model Context Protocol (MCP).

---

## 🔒 Privacy & Security First

**Important:** This integration maintains Guardian Node's privacy-first principles:
- ✅ **No data leaves your home** - All processing stays local
- ✅ **Grok gets controlled access** - Only to approved family cybersecurity tools
- ✅ **Child-safe responses** - All content filtered for family use
- ✅ **Comprehensive logging** - All interactions are audited
- ✅ **Offline-first** - Guardian Node remains offline-capable

---

## 🚀 Quick Setup

### Step 1: Configure MCP in Kiro

1. **Open Kiro IDE** in your Guardian Node project
2. **Open Command Palette** (`Ctrl+Shift+P` / `Cmd+Shift+P`)
3. **Search for "MCP"** and select "Open Kiro MCP Settings"
4. **The MCP configuration is already created** at `.kiro/settings/mcp.json`

### Step 2: Install MCP Dependencies

```bash
# In your Guardian Node directory
cd guardian-node

# Install MCP support (ensure offline installation)
pip install mcp --no-deps --offline || pip install mcp

# Verify Guardian Node MCP server
python guardian_interpreter/mcp_server.py --test

# Check MCP server configuration
python -c "import json; print(json.dumps(json.load(open('.kiro/settings/mcp.json')), indent=2))"
```

### Step 3: Activate Guardian Node MCP Server

**Option 1: Docker Deployment (Recommended)**
```bash
# Start Guardian Node with MCP support
docker-compose up -d

# Verify MCP server is running
docker-compose logs guardian-node | grep "MCP server"

# Check MCP server health
curl -s http://localhost:8080/health | jq .
```

**Option 2: Direct Python Execution**
```bash
# Start Guardian Node with MCP server
cd guardian_interpreter
python main.py --mcp --family-mode

# Or start MCP server separately
python mcp_server.py --privacy-mode strict --child-safe true
```

**Option 3: Background Service**
```bash
# Start as background service
nohup python guardian_interpreter/mcp_server.py > logs/mcp_server.log 2>&1 &

# Check service status
ps aux | grep mcp_server
tail -f logs/mcp_server.log
```

### Step 4: Activate MCP in Kiro IDE

**Enable Guardian Node MCP Server:**
1. **Open Kiro Command Palette** (`Ctrl+Shift+P` / `Cmd+Shift+P`)
2. **Type "MCP"** and select "MCP: Restart Servers"
3. **Verify Connection** - Look for "guardian-node" in MCP Server panel
4. **Check Status** - Server should show "Connected" with green indicator

**Verify MCP Configuration:**
```bash
# Check MCP server status in Kiro
# Command Palette > "MCP: Show Server Status"

# Or verify manually
curl -s http://localhost:8080/mcp/status
```

### Step 5: Test the Connection

**Basic Connection Test:**
```
Ask Grok: "Using Guardian Node, what is your current status?"
```

**Family Safety Test:**
```
Ask Grok: "Using Guardian Node, how can I keep my family safe online?"
```

**Skill Execution Test:**
```
Ask Grok: "Using Guardian Node, run a password check on 'mypassword123'"
```

**Expected Response Indicators:**
- ✅ Grok mentions "Guardian Node" in responses
- ✅ Family-friendly, educational tone
- ✅ Privacy-first language ("offline", "local processing")
- ✅ Specific Guardian Node tool results

---

## 🛠️ Available Tools for Grok

When connected, Grok will have access to these Guardian Node capabilities:

### 🏠 Family Cybersecurity Tools

1. **`ask_family_question`**
   - Ask family cybersecurity questions
   - Get age-appropriate, educational responses
   - Example: "How do I explain phishing to my 10-year-old?"

2. **`run_family_skill`**
   - Execute Guardian Node security skills
   - Available skills:
     - `threat_analysis` - Analyze security threats
     - `password_check` - Check password strength
     - `device_scan` - Scan family devices
     - `parental_control_check` - Verify parental controls
     - `phishing_education` - Learn about phishing
     - `network_security_audit` - Audit network security

3. **`get_security_recommendations`**
   - Get personalized family security recommendations
   - Customized for family size and children

4. **`analyze_family_security`**
   - Comprehensive family security analysis
   - Security score and detailed findings

### 📊 Guardian Node Resources

- **Guardian Status** - Current system health and capabilities
- **Family Skills** - Available cybersecurity tools
- **Security Recommendations** - Personalized advice
- **Log Summary** - Privacy-filtered activity summary

---

## 💬 Family-Safe Query Examples

### Teaching Kids About Online Safety

**You:** "Grok, using Guardian Node, help me explain internet safety to my 8-year-old."

**Grok:** *Uses Guardian Node's `ask_family_question` tool*

"Based on Guardian Node's family cybersecurity expertise, here's how to explain internet safety to an 8-year-old:

**Use Simple Analogies:**
- The internet is like a big city with good and bad neighborhoods
- Passwords are like keys to your house - keep them secret
- Strangers online are still strangers, just like in real life

**Guardian Node recommends these age-appropriate topics:**
1. Never share personal information (name, address, school)
2. Tell a grown-up if something online makes you uncomfortable
3. Only visit websites that parents approve

Would you like me to run Guardian Node's phishing education module for more specific guidance?"

### Age-Appropriate Cybersecurity Education

**You:** "Grok, using Guardian Node, what cybersecurity concepts should I teach my teenager?"

**Grok:** *Uses Guardian Node's `ask_family_question` with age_appropriate=true*

"Guardian Node's family assistant recommends these cybersecurity concepts for teenagers:

**Essential Skills for Teens:**
1. **Password Management** - Using unique, strong passwords and password managers
2. **Social Media Privacy** - Understanding privacy settings and digital footprints
3. **Phishing Recognition** - Identifying suspicious emails, texts, and websites
4. **Safe Downloading** - Avoiding malware through careful software choices
5. **Digital Citizenship** - Understanding online behavior consequences

**Teaching Approach:**
- Use real-world examples they can relate to
- Explain the 'why' behind security rules
- Practice identifying threats together
- Gradually increase their security responsibilities

**Guardian Node Note:** All guidance is filtered for family-appropriate content and focuses on education rather than fear."

### Password Security Check

**You:** "Grok, check if 'mypassword123' is secure using Guardian Node."

**Grok:** *Uses Guardian Node's `run_family_skill` with `password_check`*

"Guardian Node's password analysis results:

**Password Strength: Weak (25/100)**

**Issues Found:**
- No uppercase letters
- No special characters
- Common word pattern
- Predictable number sequence

**Guardian Node Recommendations:**
- Use at least 12 characters
- Include uppercase, lowercase, numbers, and symbols
- Avoid dictionary words
- Consider using a password manager

Would you like Guardian Node to generate family password security recommendations?"

### Family Security Analysis

**You:** "Grok, run a complete family security analysis using Guardian Node."

**Grok:** *Uses Guardian Node's `analyze_family_security` tool*

"Guardian Node Family Security Analysis Complete:

**Overall Security Score: 87.0/100** ✅

**Security Findings:**
✅ Password policies are enforced
✅ Parental controls are active  
✅ Network security is properly configured
✅ Device security is up to date

**Priority Recommendations:**
1. 🔴 Enable two-factor authentication (High Priority)
2. 🟡 Update router firmware (Medium Priority)
3. 🟡 Review social media privacy settings (Medium Priority)

**Privacy Note:** This analysis was performed completely offline with no external data sharing."

### Device Security Guidance

**You:** "Grok, using Guardian Node, how do I secure my family's smartphones?"

**Grok:** *Uses Guardian Node's `run_family_skill` with device_scan*

"Guardian Node's device security guidance for family smartphones:

**Essential Smartphone Security Steps:**

**For Parents:**
1. **Enable Screen Locks** - Use PIN, pattern, fingerprint, or face unlock
2. **Keep Software Updated** - Enable automatic security updates
3. **Review App Permissions** - Regularly check what apps can access
4. **Use Find My Device** - Enable location services for lost devices
5. **Backup Important Data** - Regular backups to secure locations

**For Children's Devices:**
1. **Parental Controls** - Use built-in screen time and app restrictions
2. **Safe Browsing** - Enable safe search and content filters
3. **App Store Restrictions** - Require approval for app downloads
4. **Location Sharing** - Configure family location sharing appropriately
5. **Emergency Contacts** - Ensure emergency contacts are easily accessible

**Guardian Node Recommendation:** Start with basic security (screen locks, updates) then gradually add more advanced features as family members become comfortable with them."

### Phishing Education for Families

**You:** "Grok, using Guardian Node, teach my family about phishing attacks."

**Grok:** *Uses Guardian Node's `run_family_skill` with phishing_education*

"Guardian Node's Family Phishing Education:

**What is Phishing? (Family-Friendly Explanation)**
Phishing is like digital fishing - bad actors use fake 'bait' (emails, texts, websites) to 'catch' your personal information.

**Common Phishing Examples:**
1. **Fake Bank Emails** - 'Your account is locked, click here to unlock'
2. **Prize Scams** - 'You've won! Just enter your details to claim'
3. **Urgent Messages** - 'Your account expires today, act now!'
4. **Fake Tech Support** - 'Your computer is infected, call this number'

**Family Protection Strategies:**
- **Stop and Think** - If it seems urgent or too good to be true, it probably is
- **Verify Independently** - Contact companies directly using official numbers
- **Check URLs Carefully** - Look for misspellings or suspicious domains
- **Never Give Personal Info** - Legitimate companies won't ask for passwords via email

**Practice Activity:** Guardian Node suggests creating a family game where you identify phishing attempts together, making it educational rather than scary for children."

---

## ⚙️ Configuration Options

### MCP Server Settings

The Guardian Node MCP server can be configured in `.kiro/settings/mcp.json`:

```json
{
  "mcpServers": {
    "guardian-node": {
      "command": "python",
      "args": [
        "-m", "guardian_interpreter.mcp_server",
        "--privacy-mode", "strict",
        "--child-safe", "true"
      ],
      "env": {
        "GUARDIAN_OFFLINE": "true",
        "GUARDIAN_PRIVACY_MODE": "strict"
      },
      "autoApprove": [
        "ask_family_question",
        "get_security_recommendations",
        "guardian_status"
      ]
    }
  }
}
```

### Privacy Controls

- **`--privacy-mode strict`** - Maximum privacy protection
- **`--child-safe true`** - All responses filtered for children
- **`GUARDIAN_OFFLINE true`** - Ensures no external network calls
- **`autoApprove`** - Tools that don't require confirmation

---

## 🔍 Monitoring & Logging

### Check MCP Connection Status

```bash
# In Kiro Command Palette
"MCP: Show Server Status"

# Or check logs
tail -f guardian-node/logs/guardian.log | grep MCP
```

### View Guardian Node Activity

```bash
# Check Guardian Node logs
docker-compose logs -f guardian-node

# Check MCP-specific logs
tail -f guardian-node/logs/mcp_server.log
```

### Audit Trail

All Grok interactions with Guardian Node are logged:
- **User queries** - What questions were asked
- **Tool executions** - Which Guardian Node tools were used
- **Responses** - What information was provided
- **Privacy events** - Any blocked or filtered content

---

## 🛡️ Security Features

### What Grok CAN Access
- ✅ Family cybersecurity education content
- ✅ Security analysis tools (threat analysis, password checking)
- ✅ Family-safe recommendations and tips
- ✅ General Guardian Node status information

### What Grok CANNOT Access
- ❌ Personal family data or profiles
- ❌ Detailed system logs or sensitive information
- ❌ Network configuration details
- ❌ Any external network access through Guardian Node
- ❌ Raw system commands or administrative functions

### Privacy Protections
- **Local Processing Only** - All Guardian Node processing stays on your device
- **No Data Transmission** - Guardian Node never sends data externally
- **Child-Safe Filtering** - All responses appropriate for family use
- **Audit Logging** - Complete record of all interactions
- **Controlled Access** - Only approved tools and information available

---

## 🔧 Comprehensive Troubleshooting Guide

### MCP Server Connection Issues

**Problem: MCP Server Won't Start**

**Diagnosis Steps:**
```bash
# 1. Check Guardian Node is running
docker-compose ps
# Expected: guardian-node container should be "Up"

# 2. Check Python dependencies
pip list | grep mcp
# Expected: mcp package should be installed

# 3. Test MCP server directly
cd guardian-node/guardian_interpreter
python mcp_server.py --test
# Expected: "MCP server test successful" message

# 4. Check port availability
netstat -tulpn | grep 8080
# Expected: Port 8080 should be available or used by Guardian Node
```

**Common Solutions:**
```bash
# Install missing MCP dependency
pip install mcp

# Fix port conflicts
docker-compose down && docker-compose up -d

# Reset MCP server
pkill -f mcp_server && python guardian_interpreter/mcp_server.py &
```

### Kiro IDE Integration Issues

**Problem: Grok Can't See Guardian Node Tools**

**Diagnosis Steps:**
1. **Check MCP Configuration**
   ```bash
   # Verify .kiro/settings/mcp.json exists and is valid
   cat .kiro/settings/mcp.json | python -m json.tool
   # Expected: Valid JSON with guardian-node server configuration
   ```

2. **Verify Server Status in Kiro**
   - Open Command Palette (`Ctrl+Shift+P`)
   - Type "MCP: Show Server Status"
   - Look for "guardian-node" with "Connected" status

3. **Check MCP Server Logs**
   ```bash
   # Check Kiro MCP logs
   tail -f ~/.kiro/logs/mcp.log
   
   # Check Guardian Node MCP logs
   tail -f guardian-node/logs/mcp_server.log
   
   # Check Guardian Node main logs
   tail -f guardian-node/logs/guardian.log | grep MCP
   ```

**Common Solutions:**
```bash
# Restart MCP servers in Kiro
# Command Palette > "MCP: Restart Servers"

# Reload Kiro window
# Command Palette > "Developer: Reload Window"

# Reset MCP configuration
cp guardian-node/.kiro/settings/mcp.json.backup guardian-node/.kiro/settings/mcp.json
```

### Permission and Access Issues

**Problem: Permission Denied Errors**

**Diagnosis Steps:**
```bash
# Check file permissions
ls -la guardian-node/guardian_interpreter/mcp_server.py
# Expected: File should be executable

# Check Docker permissions
docker-compose exec guardian-node ls -la /app
# Expected: App directory should be accessible

# Check log file permissions
ls -la guardian-node/logs/
# Expected: Log files should be writable
```

**Solutions:**
```bash
# Fix file permissions
chmod +x guardian-node/guardian_interpreter/mcp_server.py
chmod -R 755 guardian-node/guardian_interpreter/

# Fix Docker permissions
docker-compose exec guardian-node chown -R app:app /app
docker-compose restart guardian-node

# Fix log permissions
mkdir -p guardian-node/logs
chmod 755 guardian-node/logs
```

### Network and Connectivity Issues

**Problem: MCP Server Not Responding**

**Diagnosis Steps:**
```bash
# Test local connectivity
curl -s http://localhost:8080/health
# Expected: JSON response with Guardian Node status

# Check if Guardian Node is blocking connections
grep "blocked" guardian-node/logs/blocked_calls.log
# Expected: No MCP-related blocks (MCP should be allowed locally)

# Verify offline mode is working
grep "GUARDIAN_OFFLINE" guardian-node/logs/guardian.log
# Expected: Offline mode should be enabled
```

**Solutions:**
```bash
# Allow local MCP connections
echo "127.0.0.1 localhost" >> /etc/hosts

# Restart with network debugging
docker-compose down
GUARDIAN_DEBUG=true docker-compose up -d

# Check firewall settings
sudo ufw status | grep 8080
# Add rule if needed: sudo ufw allow 8080/tcp
```

### Family Assistant Integration Issues

**Problem: Family Skills Not Working**

**Diagnosis Steps:**
```bash
# Test family assistant directly
cd guardian-node/guardian_interpreter
python -c "from family_assistant.family_assistant_manager import FamilyAssistantManager; fm = FamilyAssistantManager(); print('Family Assistant OK')"

# Check family skills registration
python -c "from family_assistant.skill_registry import FamilySkillRegistry; print(FamilySkillRegistry().list_skills())"

# Test MCP family tools
curl -X POST http://localhost:8080/mcp/tools/ask_family_question \
  -H "Content-Type: application/json" \
  -d '{"question": "test"}'
```

**Solutions:**
```bash
# Reinstall family assistant dependencies
pip install -r guardian-node/guardian_interpreter/requirements.txt

# Reset family assistant configuration
cp guardian-node/config/family_assistant.yaml.default guardian-node/config/family_assistant.yaml

# Restart with family mode enabled
docker-compose down
GUARDIAN_FAMILY_MODE=true docker-compose up -d
```

### Advanced Debugging

**Problem: Intermittent Connection Issues**

**Enable Debug Logging:**
```bash
# Enable comprehensive logging
export GUARDIAN_DEBUG=true
export MCP_DEBUG=true

# Start with verbose logging
python guardian_interpreter/mcp_server.py --debug --verbose

# Monitor all logs simultaneously
tail -f guardian-node/logs/*.log
```

**Performance Diagnostics:**
```bash
# Check resource usage
docker stats guardian-node

# Monitor MCP server performance
ps aux | grep mcp_server
top -p $(pgrep -f mcp_server)

# Check memory usage
free -h
df -h
```

**Network Diagnostics:**
```bash
# Test MCP protocol directly
echo '{"jsonrpc": "2.0", "method": "initialize", "id": 1}' | nc localhost 8080

# Check for port conflicts
lsof -i :8080

# Verify localhost resolution
nslookup localhost
ping -c 1 localhost
```

### Error Code Reference

**Common MCP Error Codes:**
- **-32700**: Parse error (Invalid JSON)
- **-32600**: Invalid Request (Malformed MCP request)
- **-32601**: Method not found (Tool/resource not available)
- **-32602**: Invalid params (Wrong parameters for tool)
- **-32603**: Internal error (Guardian Node internal error)

**Guardian Node Specific Errors:**
- **GUARDIAN_001**: Family Assistant not initialized
- **GUARDIAN_002**: Skill execution failed
- **GUARDIAN_003**: Privacy mode violation detected
- **GUARDIAN_004**: Child safety filter triggered
- **GUARDIAN_005**: Offline mode network block

### Family-Friendly Troubleshooting

**"Grok doesn't seem to know about Guardian Node"**

**Simple Checks:**
1. **Is Guardian Node running?**
   - Look for the Guardian Node icon in your system tray
   - Or check: `docker-compose ps` (should show "Up")

2. **Is Kiro connected to Guardian Node?**
   - In Kiro, press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
   - Type "MCP" and select "Show Server Status"
   - Look for "guardian-node" with green "Connected" status

3. **Test with a simple question:**
   ```
   Ask Grok: "Using Guardian Node, what is your status?"
   ```
   - Grok should mention Guardian Node in the response

**"Guardian Node seems slow or unresponsive"**

**Quick Fixes:**
```bash
# Restart Guardian Node
docker-compose restart guardian-node

# Or restart everything
docker-compose down && docker-compose up -d

# Check if your computer has enough memory
free -h  # On Linux/Mac
# Should have at least 2GB available
```

**"I'm getting privacy or security warnings"**

**This is Normal and Good!**
- Guardian Node is designed to be privacy-first
- It blocks external internet connections by design
- All processing happens locally on your device
- These warnings confirm your privacy is protected

**If you see errors about "blocked calls" - this is working correctly!**

### Getting Additional Help

**For Families - Simple Log Collection:**
```bash
# Easy way to collect logs for support
mkdir ~/guardian-help
cp guardian-node/logs/guardian.log ~/guardian-help/
cp ~/.kiro/logs/mcp.log ~/guardian-help/ 2>/dev/null || echo "No Kiro MCP log found"

# Zip everything up
zip -r guardian-help-$(date +%Y%m%d).zip ~/guardian-help/
```

**What to Include When Asking for Help:**
1. **What you were trying to do** - "I asked Grok to help with family passwords"
2. **What happened instead** - "Grok said it couldn't connect to Guardian Node"
3. **Your setup** - "Running on Raspberry Pi with Docker" or "Windows with direct Python"
4. **Any error messages** - Copy the exact text you see

**System Information for Support:**
```bash
# Quick system check
echo "=== Guardian Node Help Info ===" > guardian-info.txt
echo "Date: $(date)" >> guardian-info.txt
echo "System: $(uname -a)" >> guardian-info.txt
echo "Python: $(python --version)" >> guardian-info.txt
echo "Docker: $(docker --version 2>/dev/null || echo 'Not using Docker')" >> guardian-info.txt
echo "Guardian Node Status:" >> guardian-info.txt
docker-compose ps >> guardian-info.txt 2>/dev/null || echo "Not using Docker Compose" >> guardian-info.txt
```

**Privacy Note:** All logs and system information stay on your device unless you choose to share them for support. Guardian Node never sends any data externally.

---

## 🎯 Best Practices for Families

### Effective Family Cybersecurity Queries

**Start with Educational Questions:**
```
"Using Guardian Node, how do I teach my child about password safety?"
"Using Guardian Node, what should my family know about online privacy?"
"Using Guardian Node, help me explain why we need antivirus software"
```

**Ask for Age-Appropriate Guidance:**
```
"Using Guardian Node, what cybersecurity concepts should I teach my 8-year-old?"
"Using Guardian Node, how do I talk to my teenager about social media safety?"
"Using Guardian Node, what online safety rules should our family have?"
```

**Request Practical, Actionable Advice:**
```
"Using Guardian Node, create a family internet safety checklist"
"Using Guardian Node, how do we secure our home WiFi for kids?"
"Using Guardian Node, what parental controls should we use?"
```

**Use Guardian Node for Family Security Analysis:**
```
"Using Guardian Node, analyze our family's current security setup"
"Using Guardian Node, what are our biggest cybersecurity risks?"
"Using Guardian Node, prioritize security improvements for our family"
```

### Privacy-First Practices

**What Guardian Node Does for Your Privacy:**
1. **All Processing Local** - Nothing leaves your home network
2. **No Data Collection** - Guardian Node doesn't store or share your conversations
3. **Child-Safe Filtering** - All responses are appropriate for family use
4. **Comprehensive Logging** - You can review exactly what information was accessed

**Family Privacy Guidelines:**
1. **Review Logs Regularly** - Check `guardian-node/logs/` to see what was accessed
2. **Use Auto-Approve Carefully** - Only auto-approve tools you fully trust
3. **Monitor Network Activity** - Guardian Node should never make external calls
4. **Keep Guardian Node Updated** - Get latest security patches and features

**Teaching Kids About AI Privacy:**
- Explain that Guardian Node is "our family's AI" that stays in our house
- Show them how it's different from cloud AI services
- Demonstrate the offline operation by disconnecting internet
- Use it as a teaching tool about privacy-respecting technology

### Family Learning Strategies

**Make Cybersecurity Fun:**
```
"Using Guardian Node, create a cybersecurity game for our family"
"Using Guardian Node, give us a family phishing quiz"
"Using Guardian Node, help us practice identifying safe websites"
```

**Regular Family Security Reviews:**
- **Weekly**: Ask Guardian Node for quick security tips
- **Monthly**: Run family security analysis
- **Quarterly**: Review and update family cybersecurity rules
- **Annually**: Comprehensive security posture assessment

**Age-Appropriate Learning Paths:**

**Ages 5-8: Basic Digital Safety**
```
"Using Guardian Node, how do I teach basic internet safety to young children?"
"Using Guardian Node, what are simple online safety rules for kindergarteners?"
```

**Ages 9-12: Expanding Digital Literacy**
```
"Using Guardian Node, what cybersecurity concepts should preteens understand?"
"Using Guardian Node, how do I teach password creation to elementary students?"
```

**Ages 13-17: Advanced Digital Citizenship**
```
"Using Guardian Node, what advanced cybersecurity should teenagers know?"
"Using Guardian Node, how do I discuss social media privacy with teens?"
```

**Adults: Ongoing Education**
```
"Using Guardian Node, what are current cybersecurity threats for parents?"
"Using Guardian Node, how do I stay updated on family cybersecurity?"
```

### Technical Best Practices

**For Families Using Guardian Node:**
1. **Start Simple** - Begin with basic questions before complex analysis
2. **Regular Updates** - Keep Guardian Node updated for latest protections
3. **Backup Important Data** - Guardian Node protects, but backups are still important
4. **Test Offline Mode** - Occasionally disconnect internet to verify offline operation

**For IT-Savvy Family Members:**
1. **Monitor Resource Usage** - Guardian Node should be lightweight on your system
2. **Review MCP Logs** - Check `~/.kiro/logs/mcp.log` for any issues
3. **Validate Responses** - Ensure all Guardian Node responses are family-appropriate
4. **Customize Auto-Approve** - Adjust which tools don't require manual approval

**For Developers Extending Guardian Node:**
1. **Test in Family Mode** - Always test new features with child-safe filtering enabled
2. **Document New Tools** - If adding MCP capabilities, document for family use
3. **Privacy Impact Assessment** - Ensure new features maintain offline-first operation
4. **Family Testing** - Get feedback from actual families using your extensions

---

## 📚 Advanced Usage

### Custom Family Profiles

You can customize Guardian Node's responses for your specific family:

```python
# In guardian_interpreter/mcp_server.py
# Modify the family profile creation:

profile = FamilySecurityProfile()
profile.family_name = "Your Family Name"
profile.members = [
    {"name": "Parent1", "role": "admin", "tech_level": "advanced"},
    {"name": "Parent2", "role": "admin", "tech_level": "intermediate"},
    {"name": "Child1", "age": 12, "role": "child", "tech_level": "beginner"},
    {"name": "Child2", "age": 8, "role": "child", "tech_level": "beginner"}
]
```

### Adding Custom Skills

To add new family cybersecurity skills that Grok can access:

1. **Create the skill** in `guardian_interpreter/skills/`
2. **Register it** in the family manager
3. **Add to MCP tools** in `mcp_server.py`
4. **Update auto-approve list** if appropriate

---

## 🤝 Support

### Getting Help
- **Documentation** - Check Guardian Node docs in `docs/`
- **Logs** - Review MCP and Guardian Node logs
- **Community** - Guardian Node GitHub discussions
- **Kiro Support** - Kiro IDE documentation and support

### Reporting Issues
- **Privacy Concerns** - Report immediately if any data leaks detected
- **Family Safety** - Report inappropriate content or responses
- **Technical Issues** - Include logs and configuration details
- **Feature Requests** - Suggest new family cybersecurity capabilities

---

## 🛡️ Family-Safe Response Filtering

### What Makes Responses Family-Safe?

**Content Filtering Features:**
- **Age-Appropriate Language** - Technical terms explained in simple language
- **Educational Focus** - Emphasis on learning rather than fear
- **Positive Framing** - Solutions-oriented rather than problem-focused
- **No Scary Details** - Threat explanations without frightening specifics
- **Actionable Guidance** - Practical steps families can actually take

### Expected Response Characteristics

**Family-Friendly Tone:**
```
✅ "Here's how to keep your family safe online..."
✅ "Let's learn about password security together..."
✅ "Guardian Node recommends these family-friendly steps..."

❌ "Your system is vulnerable to advanced persistent threats..."
❌ "Hackers can exploit zero-day vulnerabilities to..."
❌ "Critical security breach detected in your network..."
```

**Educational Approach:**
```
✅ "Think of passwords like keys to your house - you want them to be strong and unique"
✅ "Phishing emails are like digital fishing - they use fake bait to catch your information"
✅ "Antivirus software is like a security guard for your computer"

❌ "Implement multi-factor authentication protocols"
❌ "Configure intrusion detection systems"
❌ "Deploy endpoint protection platforms"
```

**Child-Safe Examples:**
```
✅ "Some websites aren't appropriate for children, just like some places in the real world"
✅ "It's important to tell a grown-up if something online makes you uncomfortable"
✅ "Never share personal information with people you don't know online"

❌ Detailed descriptions of online predators
❌ Graphic examples of cyberbullying
❌ Explicit threat scenarios
```

### Quality Assurance Indicators

**Look for These in Guardian Node Responses:**
- 🎓 **Educational tone** - Teaching rather than warning
- 👨‍👩‍👧‍👦 **Family context** - Relevant to household situations
- 🔒 **Privacy emphasis** - Mentions offline/local processing
- ✅ **Actionable steps** - Clear, doable recommendations
- 🛡️ **Guardian Node branding** - References to Guardian Node tools and analysis

**Red Flags (Should Not Appear):**
- ❌ Technical jargon without explanation
- ❌ Fear-based messaging
- ❌ Inappropriate content for children
- ❌ References to external services or cloud processing
- ❌ Overly complex technical procedures

### Customizing Family Safety Levels

**Standard Family Mode (Default):**
- Appropriate for mixed-age families
- Balances education with simplicity
- Suitable for children 8+ with parent guidance

**Child-Safe Mode (Strict):**
- Extra filtering for very young children
- Simplified language and concepts
- No potentially scary scenarios

**Teen Mode (Advanced):**
- More detailed technical information
- Preparation for adult digital responsibility
- Advanced privacy and security concepts

**Configuration Example:**
```json
{
  "family_assistant": {
    "safety_level": "standard",
    "child_safe_mode": true,
    "max_complexity": "intermediate",
    "filter_scary_content": true,
    "educational_focus": true
  }
}
```

---

**Guardian Node + Grok + Kiro = Powerful, Private Family Cybersecurity! 🛡️**

*Your family's digital safety, enhanced by AI, protected by privacy.*

---

## 📋 Quick Reference

### Essential Grok Commands for Families
```
"Using Guardian Node, how can I keep my family safe online?"
"Using Guardian Node, teach my child about password security"
"Using Guardian Node, analyze our family's security posture"
"Using Guardian Node, what are current cybersecurity threats for families?"
"Using Guardian Node, help me secure our home network"
```

### MCP Server Status Check
```bash
# Quick health check
curl -s http://localhost:8080/health | jq .

# Restart if needed
docker-compose restart guardian-node
```

### Emergency Troubleshooting
```bash
# If Grok can't connect to Guardian Node:
# 1. Restart MCP servers in Kiro (Command Palette > "MCP: Restart Servers")
# 2. Restart Guardian Node (docker-compose restart guardian-node)
# 3. Check logs (tail -f guardian-node/logs/guardian.log)
```

**Remember: Guardian Node keeps your family's cybersecurity conversations completely private and offline! 🏠🔒**
=======
# grok-kiro-integration.md expanded guide...
>>>>>>> a0d2c75a88747ce742b9ef6cc664642fcb07ac5e
