#!/usr/bin/env python3
"""
ProjectMeats3 Post-Deployment Health Check

Quick script to verify deployment is working correctly.
Can be run locally or in CI/CD after deployment.

Environment Priority:
    Primary staging environment: uat.meatscentral.com (UAT)
    Legacy staging: staging.meatscentral.com (DEPRECATED - use UAT instead)
    Production: meatscentral.com

Usage:
    python health_check.py https://uat.meatscentral.com
    python health_check.py https://projectmeats.app --verbose
"""

import sys
import requests
import argparse
from urllib.parse import urljoin
import json
from typing import Dict, List, Optional

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'


def log(message: str, level: str = "INFO"):
    """Log a message with color coding"""
    color_map = {
        "INFO": Colors.BLUE,
        "SUCCESS": Colors.GREEN,
        "WARNING": Colors.YELLOW,
        "ERROR": Colors.RED
    }
    color = color_map.get(level, '')
    print(f"{color}{message}{Colors.END}")


def check_endpoint(base_url: str, endpoint: str, expected_status: int = 200, timeout: int = 10) -> Dict:
    """Check a single endpoint"""
    url = urljoin(base_url, endpoint)
    try:
        response = requests.get(url, timeout=timeout, allow_redirects=True)
        success = response.status_code == expected_status
        
        return {
            "endpoint": endpoint,
            "url": url,
            "status_code": response.status_code,
            "expected_status": expected_status,
            "success": success,
            "response_time": response.elapsed.total_seconds(),
            "content_length": len(response.content) if response.content else 0
        }
    except requests.exceptions.Timeout:
        return {
            "endpoint": endpoint,
            "url": url,
            "success": False,
            "error": "Timeout"
        }
    except requests.exceptions.ConnectionError:
        return {
            "endpoint": endpoint,
            "url": url,
            "success": False,
            "error": "Connection Error"
        }
    except Exception as e:
        return {
            "endpoint": endpoint,
            "url": url,
            "success": False,
            "error": str(e)
        }


def run_health_checks(base_url: str, verbose: bool = False) -> bool:
    """Run comprehensive health checks"""
    log(f"{Colors.BOLD}ProjectMeats3 Health Check{Colors.END}")
    log(f"Testing: {base_url}")
    
    # Check if using deprecated staging domain and log warning
    if "staging.meatscentral.com" in base_url.lower():
        log("⚠️  WARNING: staging.meatscentral.com is DEPRECATED", "WARNING")
        log("   Please use uat.meatscentral.com as the primary middle environment", "WARNING")
        log("   UAT is the active staging environment per pipeline configuration", "WARNING")
    elif "uat.meatscentral.com" in base_url.lower():
        log("✓  Using UAT environment (uat.meatscentral.com) - Primary middle environment", "SUCCESS")
    
    log("-" * 50)
    
    # Define endpoints to check
    endpoints = [
        {"path": "/", "name": "Frontend", "status": 200},
        {"path": "/api/v1/", "name": "API Root", "status": 200},
        {"path": "/api/v1/health/", "name": "Health Endpoint", "status": 200},
        {"path": "/admin/", "name": "Admin Panel", "status": 302},  # Redirect to login
        {"path": "/static/admin/css/base.css", "name": "Static Files", "status": 200},
    ]
    
    results = []
    all_passed = True
    
    for endpoint_config in endpoints:
        result = check_endpoint(
            base_url, 
            endpoint_config["path"], 
            endpoint_config["status"]
        )
        result["name"] = endpoint_config["name"]
        results.append(result)
        
        if result["success"]:
            status_msg = f"✅ {result['name']}"
            if verbose and 'response_time' in result:
                status_msg += f" ({result['response_time']:.2f}s)"
            log(status_msg, "SUCCESS")
        else:
            error_msg = result.get("error", f"HTTP {result.get('status_code', 'Unknown')}")
            log(f"❌ {result['name']}: {error_msg}", "ERROR")
            all_passed = False
    
    log("-" * 50)
    
    # Summary
    passed = sum(1 for r in results if r["success"])
    total = len(results)
    
    if all_passed:
        log(f"🎉 All checks passed! ({passed}/{total})", "SUCCESS")
        log("Your ProjectMeats3 deployment is healthy and ready!", "SUCCESS")
    else:
        log(f"❌ Some checks failed ({passed}/{total})", "ERROR")
        log("Please review the errors above and check your deployment configuration.", "ERROR")
    
    if verbose:
        log("\nDetailed Results:")
        for result in results:
            print(json.dumps(result, indent=2))
    
    return all_passed


def main():
    parser = argparse.ArgumentParser(
        description="ProjectMeats3 Post-Deployment Health Check",
        epilog="Example: python health_check.py https://your-app.ondigitalocean.app"
    )
    
    parser.add_argument(
        'url',
        help='Base URL of your deployed application'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed results'
    )
    
    parser.add_argument(
        '--timeout',
        type=int,
        default=10,
        help='Request timeout in seconds (default: 10)'
    )
    
    args = parser.parse_args()
    
    # Ensure URL has protocol
    url = args.url
    if not url.startswith(('http://', 'https://')):
        url = f'https://{url}'
    
    success = run_health_checks(url, args.verbose)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()