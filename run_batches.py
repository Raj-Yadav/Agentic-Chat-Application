
import os
import subprocess
import time

def run_batches():
    # Find all test_batch_X.py files
    batch_files = [f for f in os.listdir('.') if f.startswith('test_batch_') and f.endswith('.py')]
    
    # Sort them by number (assuming format test_batch_X.py)
    batch_files.sort(key=lambda x: int(x.split('_')[2].split('.')[0]))
    
    print(f"Found {len(batch_files)} batch files to run.")
    
    # Remove old report if exists to start fresh
    if os.path.exists("test_report_full.md"):
        os.remove("test_report_full.md")
        print("Removed old test_report_full.md")
        
    for batch_file in batch_files:
        print(f"\nExample running: {batch_file}...")
        try:
            # Run the batch script
            result = subprocess.run(["python", batch_file], capture_output=True, text=True)
            
            # Print output to console
            print(result.stdout)
            
            if result.returncode != 0:
                print(f"Error running {batch_file}:")
                print(result.stderr)
            
            # small delay between batches
            time.sleep(2)
            
        except Exception as e:
            print(f"Failed to run {batch_file}: {e}")

    print("\nAll batches completed. Check test_report_full.md for results.")

if __name__ == "__main__":
    run_batches()
