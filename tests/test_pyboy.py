from pyboy import PyBoy
import time

ROM_PATH = "roms/crystal.gbc"

def main():
    print("Testing PyBoy standalone...")
    try:
        pyboy = PyBoy(ROM_PATH, window="SDL2")
        pyboy.set_emulation_speed(0)
        print("PyBoy initialized. Running for 300 frames...")
        
        for i in range(300):
            pyboy.tick()
            if i % 60 == 0:
                print(f"Frame {i}")
            time.sleep(0.01)
            
        print("PyBoy test completed successfully.")
        pyboy.stop()
    except Exception as e:
        print(f"PyBoy crashed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
