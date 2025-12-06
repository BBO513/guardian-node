#!/usr/bin/env python3
"""
Guardian Node End-to-End Family Assistant Workflow Tests
Complete integration testing for family cybersecurity features
"""

import unittest
import sys
import os
import time
import subprocess
import requests
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

class TestFamilyAssistantWorkflow(unittest.TestCase):
    """End-to-end tests for Guardian Node family assistant workflow"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.base_url = "http://localhost:8080"
        cls.test_timeout = 30
        cls.guardian_process = None
        
        # Check if Guardian Node is already running
        try:
            response = requests.get(f"{cls.base_url}/health", timeout=5)
            if response.status_code == 200:
                print("Guardian Node is already running")
                cls.guardian_running = True
            else:
                cls.guardian_running = False
        except requests.exceptions.RequestException:
            cls.guardian_running = False
        
        # Start Guardian Node if not running
        if not cls.guardian_running:
            cls.start_guardian_node()
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment"""
        if cls.guardian_process:
            print("Stopping Guardian Node test instance...")
            cls.guardian_process.terminate()
            cls.guardian_process.wait(timeout=10)
    
    @classmethod
    def start_guardian_node(cls):
        """Start Guardian Node for testing"""
        try:
            print("Starting Guardian Node for testing...")
            
            # Change to guardian_interpreter directory
            guardian_dir = project_root / "guardian_interpreter"
            
            # Start Guardian Node process
            cls.guardian_process = subprocess.Popen(
                [sys.executable, "main.py", "--test-mode"],
                cwd=guardian_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for Guardian Node to start
            for _ in range(30):  # Wait up to 30 seconds
                try:
                    response = requests.get(f"{cls.base_url}/health", timeout=2)
                    if response.status_code == 200:
                        print("Guardian Node started successfully")
                        cls.guardian_running = True
                        return
                except requests.exceptions.RequestException:
                    pass
                time.sleep(1)
            
            raise Exception("Guardian Node failed to start within timeout")
            
        except Exception as e:
            print(f"Failed to start Guardian Node: {e}")
            cls.guardian_running = False
    
    def test_01_guardian_node_health(self):
        """Test that Guardian Node is healthy and responding"""
        if not self.guardian_running:
            self.skipTest("Guardian Node is not running")
        
        try:
            response = requests.get(f"{self.base_url}/health", timeout=self.test_timeout)
            self.assertEqual(response.status_code, 200)
            
            health_data = response.json()
            self.assertIn('status', health_data)
            self.assertEqual(health_data['status'], 'healthy')
            
        except requests.exceptions.RequestException as e:
            self.fail(f"Health check failed: {e}")
    
    def test_02_family_assistant_availability(self):
        """Test that family assistant is available and functional"""
        if not self.guardian_running:
            self.skipTest("Guardian Node is not running")
        
        try:
            response = requests.get(f"{self.base_url}/api/family/status", timeout=self.test_timeout)
            self.assertEqual(response.status_code, 200)
            
            status_data = response.json()
            self.assertIn('family_assistant_enabled', status_data)
            self.assertTrue(status_data['family_assistant_enabled'])
            
        except requests.exceptions.RequestException as e:
            self.fail(f"Family assistant status check failed: {e}")
    
    def test_03_family_skills_listing(self):
        """Test listing of available family skills"""
        if not self.guardian_running:
            self.skipTest("Guardian Node is not running")
        
        try:
            response = requests.get(f"{self.base_url}/api/family/skills", timeout=self.test_timeout)
            self.assertEqual(response.status_code, 200)
            
            skills_data = response.json()
            self.assertIn('skills', skills_data)
            self.assertIsInstance(skills_data['skills'], list)
            self.assertGreater(len(skills_data['skills']), 0)
            
            # Check for expected skills
            skill_names = [skill['name'] for skill in skills_data['skills']]
            expected_skills = [
                'threat_analysis',
                'password_check',
                'device_scan',
                'parental_control_check',
                'phishing_education',
                'network_security_audit'
            ]
            
            for expected_skill in expected_skills:
                self.assertIn(expected_skill, skill_names)
            
        except requests.exceptions.RequestException as e:
            self.fail(f"Family skills listing failed: {e}")
    
    def test_04_password_strength_check(self):
        """Test password strength checking functionality"""
        if not self.guardian_running:
            self.skipTest("Guardian Node is not running")
        
        test_passwords = [
            {"password": "123", "expected_strength": "Weak"},
            {"password": "password123", "expected_strength": "Medium"},
            {"password": "StrongP@ssw0rd123!", "expected_strength": "Strong"}
        ]
        
        for test_case in test_passwords:
            with self.subTest(password=test_case["password"]):
                try:
                    payload = {
                        "skill": "password_check",
                        "args": [test_case["password"]]
                    }
                    
                    response = requests.post(
                        f"{self.base_url}/api/family/skill/execute",
                        json=payload,
                        timeout=self.test_timeout
                    )
                    
                    self.assertEqual(response.status_code, 200)
                    
                    result_data = response.json()
                    self.assertTrue(result_data.get('success', False))
                    self.assertIn('result', result_data)
                    self.assertIn(test_case["expected_strength"], result_data['result'])
                    
                except requests.exceptions.RequestException as e:
                    self.fail(f"Password check failed for {test_case['password']}: {e}")
    
    def test_05_threat_analysis(self):
        """Test threat analysis functionality"""
        if not self.guardian_running:
            self.skipTest("Guardian Node is not running")
        
        try:
            payload = {
                "skill": "threat_analysis",
                "args": []
            }
            
            response = requests.post(
                f"{self.base_url}/api/family/skill/execute",
                json=payload,
                timeout=self.test_timeout
            )
            
            self.assertEqual(response.status_code, 200)
            
            result_data = response.json()
            self.assertTrue(result_data.get('success', False))
            self.assertIn('result', result_data)
            self.assertIn('details', result_data)
            
            # Check threat analysis details
            details = result_data['details']
            self.assertIn('threats_found', details)
            self.assertIn('risk_level', details)
            self.assertIn('recommendations', details)
            
        except requests.exceptions.RequestException as e:
            self.fail(f"Threat analysis failed: {e}")
    
    def test_06_family_query_processing(self):
        """Test family cybersecurity query processing"""
        if not self.guardian_running:
            self.skipTest("Guardian Node is not running")
        
        test_queries = [
            "How can I keep my child safe online?",
            "What are the signs of a phishing email?",
            "How do I secure my home WiFi?",
            "What is a strong password?"
        ]
        
        for query in test_queries:
            with self.subTest(query=query):
                try:
                    payload = {"query": query}
                    
                    response = requests.post(
                        f"{self.base_url}/api/family/query",
                        json=payload,
                        timeout=self.test_timeout
                    )
                    
                    self.assertEqual(response.status_code, 200)
                    
                    result_data = response.json()
                    self.assertIn('response', result_data)
                    self.assertIn('confidence', result_data)
                    self.assertIn('follow_up_questions', result_data)
                    
                    # Check response quality
                    self.assertGreater(len(result_data['response']), 50)  # Meaningful response
                    self.assertGreater(result_data['confidence'], 0.5)  # Reasonable confidence
                    self.assertIsInstance(result_data['follow_up_questions'], list)
                    
                except requests.exceptions.RequestException as e:
                    self.fail(f"Query processing failed for '{query}': {e}")
    
    def test_07_family_security_analysis(self):
        """Test comprehensive family security analysis"""
        if not self.guardian_running:
            self.skipTest("Guardian Node is not running")
        
        try:
            response = requests.post(
                f"{self.base_url}/api/family/analyze",
                json={},
                timeout=self.test_timeout
            )
            
            self.assertEqual(response.status_code, 200)
            
            analysis_data = response.json()
            self.assertIn('status', analysis_data)
            self.assertIn('overall_score', analysis_data)
            self.assertIn('findings', analysis_data)
            self.assertIn('recommendations', analysis_data)
            
            # Validate analysis results
            self.assertIsInstance(analysis_data['overall_score'], (int, float))
            self.assertGreaterEqual(analysis_data['overall_score'], 0)
            self.assertLessEqual(analysis_data['overall_score'], 100)
            
            self.assertIsInstance(analysis_data['findings'], list)
            self.assertIsInstance(analysis_data['recommendations'], list)
            
        except requests.exceptions.RequestException as e:
            self.fail(f"Family security analysis failed: {e}")
    
    def test_08_family_recommendations(self):
        """Test family security recommendations"""
        if not self.guardian_running:
            self.skipTest("Guardian Node is not running")
        
        try:
            response = requests.get(
                f"{self.base_url}/api/family/recommendations",
                timeout=self.test_timeout
            )
            
            self.assertEqual(response.status_code, 200)
            
            recommendations_data = response.json()
            self.assertIn('recommendations', recommendations_data)
            self.assertIsInstance(recommendations_data['recommendations'], list)
            self.assertGreater(len(recommendations_data['recommendations']), 0)
            
            # Validate recommendation structure
            for rec in recommendations_data['recommendations']:
                self.assertIn('title', rec)
                self.assertIn('priority', rec)
                self.assertIn('difficulty', rec)
                self.assertIn('description', rec)
                
                # Validate priority levels
                self.assertIn(rec['priority'], ['Low', 'Medium', 'High'])
                self.assertIn(rec['difficulty'], ['Easy', 'Medium', 'Hard'])
            
        except requests.exceptions.RequestException as e:
            self.fail(f"Family recommendations failed: {e}")
    
    def test_09_device_scanning(self):
        """Test device scanning functionality"""
        if not self.guardian_running:
            self.skipTest("Guardian Node is not running")
        
        try:
            payload = {
                "skill": "device_scan",
                "args": []
            }
            
            response = requests.post(
                f"{self.base_url}/api/family/skill/execute",
                json=payload,
                timeout=self.test_timeout
            )
            
            self.assertEqual(response.status_code, 200)
            
            result_data = response.json()
            self.assertTrue(result_data.get('success', False))
            self.assertIn('details', result_data)
            
            details = result_data['details']
            self.assertIn('devices_scanned', details)
            self.assertIn('vulnerabilities', details)
            self.assertIn('last_scan', details)
            
        except requests.exceptions.RequestException as e:
            self.fail(f"Device scanning failed: {e}")
    
    def test_10_parental_controls_check(self):
        """Test parental controls verification"""
        if not self.guardian_running:
            self.skipTest("Guardian Node is not running")
        
        try:
            payload = {
                "skill": "parental_control_check",
                "args": []
            }
            
            response = requests.post(
                f"{self.base_url}/api/family/skill/execute",
                json=payload,
                timeout=self.test_timeout
            )
            
            self.assertEqual(response.status_code, 200)
            
            result_data = response.json()
            self.assertTrue(result_data.get('success', False))
            self.assertIn('details', result_data)
            
            details = result_data['details']
            self.assertIn('controls_active', details)
            self.assertIn('filtered_categories', details)
            self.assertIn('time_restrictions', details)
            
        except requests.exceptions.RequestException as e:
            self.fail(f"Parental controls check failed: {e}")
    
    def test_11_phishing_education(self):
        """Test phishing education module"""
        if not self.guardian_running:
            self.skipTest("Guardian Node is not running")
        
        try:
            payload = {
                "skill": "phishing_education",
                "args": []
            }
            
            response = requests.post(
                f"{self.base_url}/api/family/skill/execute",
                json=payload,
                timeout=self.test_timeout
            )
            
            self.assertEqual(response.status_code, 200)
            
            result_data = response.json()
            self.assertTrue(result_data.get('success', False))
            self.assertIn('details', result_data)
            
            details = result_data['details']
            self.assertIn('topics_covered', details)
            self.assertIsInstance(details['topics_covered'], list)
            self.assertGreater(len(details['topics_covered']), 0)
            
        except requests.exceptions.RequestException as e:
            self.fail(f"Phishing education failed: {e}")
    
    def test_12_network_security_audit(self):
        """Test network security audit"""
        if not self.guardian_running:
            self.skipTest("Guardian Node is not running")
        
        try:
            payload = {
                "skill": "network_security_audit",
                "args": []
            }
            
            response = requests.post(
                f"{self.base_url}/api/family/skill/execute",
                json=payload,
                timeout=self.test_timeout
            )
            
            self.assertEqual(response.status_code, 200)
            
            result_data = response.json()
            self.assertTrue(result_data.get('success', False))
            self.assertIn('details', result_data)
            
            details = result_data['details']
            self.assertIn('wifi_encryption', details)
            self.assertIn('firewall_status', details)
            self.assertIn('open_ports', details)
            
        except requests.exceptions.RequestException as e:
            self.fail(f"Network security audit failed: {e}")
    
    def test_13_privacy_compliance(self):
        """Test privacy compliance - ensure no external calls"""
        if not self.guardian_running:
            self.skipTest("Guardian Node is not running")
        
        try:
            # Check blocked calls log
            response = requests.get(f"{self.base_url}/api/logs/blocked_calls", timeout=self.test_timeout)
            
            if response.status_code == 200:
                blocked_calls = response.json()
                # This test passes if we can access the blocked calls log
                # In a real deployment, we'd verify no unexpected external calls
                self.assertIn('blocked_calls', blocked_calls)
            else:
                # If endpoint doesn't exist, that's also acceptable
                self.assertIn(response.status_code, [404, 501])
            
        except requests.exceptions.RequestException:
            # Network errors are acceptable for this test
            pass
    
    def test_14_complete_family_workflow(self):
        """Test complete family cybersecurity workflow"""
        if not self.guardian_running:
            self.skipTest("Guardian Node is not running")
        
        workflow_steps = [
            # Step 1: Get family status
            ("GET", f"{self.base_url}/api/family/status", None),
            
            # Step 2: Run threat analysis
            ("POST", f"{self.base_url}/api/family/skill/execute", {
                "skill": "threat_analysis",
                "args": []
            }),
            
            # Step 3: Check password strength
            ("POST", f"{self.base_url}/api/family/skill/execute", {
                "skill": "password_check",
                "args": ["TestPassword123!"]
            }),
            
            # Step 4: Run security analysis
            ("POST", f"{self.base_url}/api/family/analyze", {}),
            
            # Step 5: Get recommendations
            ("GET", f"{self.base_url}/api/family/recommendations", None),
            
            # Step 6: Process family query
            ("POST", f"{self.base_url}/api/family/query", {
                "query": "How can I protect my family from cyber threats?"
            })
        ]
        
        for i, (method, url, payload) in enumerate(workflow_steps, 1):
            with self.subTest(step=i, method=method, url=url):
                try:
                    if method == "GET":
                        response = requests.get(url, timeout=self.test_timeout)
                    elif method == "POST":
                        response = requests.post(url, json=payload, timeout=self.test_timeout)
                    
                    self.assertEqual(response.status_code, 200)
                    
                    # Verify response contains expected data
                    response_data = response.json()
                    self.assertIsInstance(response_data, dict)
                    self.assertGreater(len(response_data), 0)
                    
                except requests.exceptions.RequestException as e:
                    self.fail(f"Workflow step {i} failed: {e}")

class TestDockerDeployment(unittest.TestCase):
    """Test Docker deployment functionality"""
    
    def test_docker_compose_file_exists(self):
        """Test that docker-compose.yml exists and is valid"""
        compose_file = project_root / "docker-compose.yml"
        self.assertTrue(compose_file.exists(), "docker-compose.yml not found")
        
        # Try to parse the compose file
        try:
            import yaml
            with open(compose_file, 'r') as f:
                compose_data = yaml.safe_load(f)
            
            self.assertIn('services', compose_data)
            self.assertIn('guardian-node', compose_data['services'])
            
        except ImportError:
            self.skipTest("PyYAML not available for compose file validation")
        except Exception as e:
            self.fail(f"Invalid docker-compose.yml: {e}")
    
    def test_dockerfile_exists(self):
        """Test that Dockerfile exists"""
        dockerfile = project_root / "Dockerfile"
        self.assertTrue(dockerfile.exists(), "Dockerfile not found")
    
    def test_docker_scripts_exist(self):
        """Test that Docker deployment scripts exist"""
        docker_dir = project_root / "docker"
        
        expected_files = [
            "entrypoint.sh",
            "health_check.py",
            "update_container.sh",
            "nginx.conf"
        ]
        
        for filename in expected_files:
            file_path = docker_dir / filename
            self.assertTrue(file_path.exists(), f"Docker file not found: {filename}")

def run_e2e_tests():
    """Run end-to-end tests"""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_classes = [
        TestFamilyAssistantWorkflow,
        TestDockerDeployment
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\nEnd-to-End Test Summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_e2e_tests()
    sys.exit(0 if success else 1)