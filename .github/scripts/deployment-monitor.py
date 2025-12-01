#!/usr/bin/env python3
"""
Deployment Monitoring Dashboard
Real-time monitoring of deployment health and status
"""

import sys
import json
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import argparse

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    END = '\033[0m'
    BOLD = '\033[1m'

def run_command(cmd: List[str]) -> Optional[str]:
    """Run shell command and return output"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return result.stdout.strip() if result.returncode == 0 else None
    except Exception as e:
        return None

def check_docker_containers() -> Dict:
    """Check status of Docker containers"""
    containers = {
        'pm-frontend': {'expected': True, 'running': False, 'health': 'unknown'},
        'pm-backend': {'expected': True, 'running': False, 'health': 'unknown'}
    }
    
    output = run_command(['docker', 'ps', '--format', '{{.Names}}|{{.Status}}'])
    if output:
        for line in output.split('\n'):
            if '|' in line:
                name, status = line.split('|', 1)
                if name in containers:
                    containers[name]['running'] = 'Up' in status
                    if 'unhealthy' in status.lower():
                        containers[name]['health'] = 'unhealthy'
                    elif 'healthy' in status.lower():
                        containers[name]['health'] = 'healthy'
                    elif 'Up' in status:
                        containers[name]['health'] = 'running'
    
    return containers

def check_disk_space() -> Dict:
    """Check available disk space"""
    output = run_command(['df', '-h', '/'])
    if output:
        lines = output.split('\n')
        if len(lines) >= 2:
            parts = lines[1].split()
            return {
                'total': parts[1],
                'used': parts[2],
                'available': parts[3],
                'use_percent': parts[4]
            }
    return {}

def check_docker_images() -> List[Dict]:
    """List recent Docker images"""
    images = []
    output = run_command(['docker', 'images', '--format', '{{.Repository}}|{{.Tag}}|{{.Size}}|{{.CreatedAt}}'])
    if output:
        for line in output.split('\n')[:10]:
            if '|' in line:
                parts = line.split('|')
                if len(parts) >= 4 and 'projectmeats' in parts[0].lower():
                    images.append({
                        'repository': parts[0],
                        'tag': parts[1],
                        'size': parts[2],
                        'created': parts[3]
                    })
    return images

def check_recent_logs(container: str, lines: int = 20) -> List[str]:
    """Get recent container logs"""
    output = run_command(['docker', 'logs', '--tail', str(lines), container])
    if output:
        return output.split('\n')[-10:]  # Last 10 lines
    return []

def check_deployment_locks() -> List[Dict]:
    """Check for active deployment locks"""
    locks = []
    output = run_command(['find', '/tmp', '-name', 'pm-deploy-*.lock', '-type', 'f'])
    if output:
        for lock_file in output.split('\n'):
            if lock_file:
                stat_output = run_command(['stat', '-c', '%Y', lock_file])
                if stat_output:
                    age = int(datetime.now().timestamp()) - int(stat_output)
                    locks.append({
                        'file': lock_file,
                        'age_seconds': age,
                        'status': 'stale' if age > 600 else 'active'
                    })
    return locks

def print_header(text: str):
    """Print formatted header"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text:^80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 80}{Colors.END}\n")

def print_section(text: str):
    """Print section header"""
    print(f"\n{Colors.BOLD}{Colors.YELLOW}▶ {text}{Colors.END}")
    print(f"{Colors.YELLOW}{'-' * 60}{Colors.END}")

def display_dashboard(environment: str = "production"):
    """Display deployment monitoring dashboard"""
    print_header(f"ProjectMeats Deployment Monitor - {environment.upper()}")
    
    # System time
    print(f"{Colors.WHITE}Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.END}")
    
    # Container Status
    print_section("Container Status")
    containers = check_docker_containers()
    for name, info in containers.items():
        status_color = Colors.GREEN if info['running'] else Colors.RED
        health_icon = "✓" if info['health'] in ['healthy', 'running'] else "✗"
        print(f"  {status_color}{health_icon} {name:20} {info['health']:15}{Colors.END}")
    
    # Disk Space
    print_section("Disk Space")
    disk = check_disk_space()
    if disk:
        use_percent = int(disk['use_percent'].rstrip('%'))
        color = Colors.RED if use_percent > 85 else Colors.YELLOW if use_percent > 70 else Colors.GREEN
        print(f"  Total:     {disk['total']}")
        print(f"  Used:      {disk['used']}")
        print(f"  Available: {disk['available']}")
        print(f"  {color}Usage:     {disk['use_percent']}{Colors.END}")
    
    # Recent Images
    print_section("Recent Docker Images")
    images = check_docker_images()
    for img in images[:5]:
        env_tag = "PROD" if "prod" in img['tag'] else "UAT" if "uat" in img['tag'] else "DEV"
        tag_color = Colors.RED if env_tag == "PROD" else Colors.YELLOW if env_tag == "UAT" else Colors.GREEN
        print(f"  {tag_color}[{env_tag}]{Colors.END} {img['repository']:50} {img['tag']:20} {img['size']:>10}")
    
    # Deployment Locks
    print_section("Deployment Locks")
    locks = check_deployment_locks()
    if locks:
        for lock in locks:
            status_color = Colors.RED if lock['status'] == 'stale' else Colors.YELLOW
            age_str = f"{lock['age_seconds']}s ago"
            print(f"  {status_color}{lock['status'].upper()}: {lock['file']} ({age_str}){Colors.END}")
    else:
        print(f"  {Colors.GREEN}✓ No active deployment locks{Colors.END}")
    
    # Recent Logs
    print_section("Recent Backend Logs (Last 5 lines)")
    backend_logs = check_recent_logs('pm-backend', 5)
    for log in backend_logs:
        if log.strip():
            # Color code by log level
            if 'ERROR' in log or 'CRITICAL' in log:
                print(f"  {Colors.RED}{log[:120]}{Colors.END}")
            elif 'WARNING' in log:
                print(f"  {Colors.YELLOW}{log[:120]}{Colors.END}")
            else:
                print(f"  {Colors.WHITE}{log[:120]}{Colors.END}")
    
    # Health Status Summary
    print_section("Deployment Health Summary")
    
    all_running = all(c['running'] for c in containers.values())
    all_healthy = all(c['health'] in ['healthy', 'running'] for c in containers.values())
    
    if all_running and all_healthy:
        print(f"  {Colors.GREEN}✓ System Status: HEALTHY{Colors.END}")
        print(f"  {Colors.GREEN}✓ All containers running and healthy{Colors.END}")
    elif all_running:
        print(f"  {Colors.YELLOW}⚠ System Status: DEGRADED{Colors.END}")
        print(f"  {Colors.YELLOW}⚠ Containers running but health checks pending{Colors.END}")
    else:
        print(f"  {Colors.RED}✗ System Status: UNHEALTHY{Colors.END}")
        print(f"  {Colors.RED}✗ One or more containers not running{Colors.END}")
    
    print(f"\n{Colors.CYAN}{'=' * 80}{Colors.END}\n")

def main():
    parser = argparse.ArgumentParser(description='ProjectMeats Deployment Monitor')
    parser.add_argument('--environment', '-e', default='production',
                      choices=['development', 'uat', 'production'],
                      help='Environment to monitor')
    parser.add_argument('--watch', '-w', action='store_true',
                      help='Continuous monitoring mode (refreshes every 10s)')
    parser.add_argument('--json', action='store_true',
                      help='Output in JSON format')
    
    args = parser.parse_args()
    
    if args.json:
        # JSON output mode
        data = {
            'timestamp': datetime.now().isoformat(),
            'environment': args.environment,
            'containers': check_docker_containers(),
            'disk': check_disk_space(),
            'images': check_docker_images()[:5],
            'locks': check_deployment_locks()
        }
        print(json.dumps(data, indent=2))
    elif args.watch:
        # Watch mode
        import time
        try:
            while True:
                subprocess.run(['clear'])
                display_dashboard(args.environment)
                print(f"{Colors.CYAN}Refreshing in 10 seconds... (Ctrl+C to exit){Colors.END}")
                time.sleep(10)
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}Monitoring stopped{Colors.END}")
    else:
        # Single display
        display_dashboard(args.environment)

if __name__ == '__main__':
    main()
