import subprocess
import sys
import os
import time
from datetime import datetime
import schedule
import threading

global_web_process = None

def run_web_interface():
    """Run the Flask web interface as a subprocess and return the process object."""
    print("Starting web interface...")
    return subprocess.Popen([sys.executable, "app.py"])

def stop_web_interface():
    global global_web_process
    if global_web_process and global_web_process.poll() is None:
        print("Stopping web interface...")
        global_web_process.terminate()
        try:
            global_web_process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            global_web_process.kill()
            global_web_process.wait()
        print("Web interface stopped.")

def start_web_interface():
    global global_web_process
    global_web_process = run_web_interface()

def run_ai_agent():
    """Run the AI agent system"""
    print("Starting Multi agent system...")
    subprocess.run([sys.executable, "main.py"])

def scheduled_ai_agent():
    """Run the AI agent at 17:00 and reload the web interface afterwards."""
    print(f"Running scheduled AI agent at {datetime.now()}")
    run_ai_agent()
    print("Reloading web interface after AI agent run...")
    stop_web_interface()
    start_web_interface()

def main():
    # Start web interface
    start_web_interface()

    # Schedule AI agent to run at 17:00
    schedule.every().day.at("17:10").do(scheduled_ai_agent)

    # Keep the main thread alive and check for scheduled tasks
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    finally:
        stop_web_interface()

if __name__ == "__main__":
    main() 
