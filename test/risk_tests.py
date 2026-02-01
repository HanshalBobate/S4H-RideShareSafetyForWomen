# run_risk_tests.py
# Run all risk tests

from test.test_risk_scenarios import RiskScenarioTester
from test.test_live_risk import LiveRiskTester

def main():
    print("\n\n")
    print("█"*60)
    print("█" + " "*58 + "█")
    print("█" + " "*18 + "RISK TESTING - MAIN MENU" + " "*16 + "█")
    print("█" + " "*58 + "█")
    print("█"*60)
    
    print("\nChoose test type:")
    print("\n1. Scenario Tests (8 realistic scenarios)")
    print("2. Live Risk Tester (manual/preset tests)")
    print("3. Both (run all tests)")
    print("4. Exit")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == "1":
        print("\nRunning Scenario Tests...")
        scenario_tester = RiskScenarioTester()
        scenario_tester.run_all_scenarios()
    
    elif choice == "2":
        print("\nRunning Live Risk Tester...")
        live_tester = LiveRiskTester()
        
        print("\nChoose mode:")
        print("1. Run preset test cases")
        print("2. Interactive mode")
        
        mode = input("\nEnter mode (1 or 2): ").strip()
        
        if mode == "1":
            live_tester.run_preset_tests()
        elif mode == "2":
            live_tester.interactive_mode()
    
    elif choice == "3":
        print("\nRunning All Tests...")
        
        print("\n" + "="*60)
        print("PART 1: SCENARIO TESTS")
        print("="*60)
        scenario_tester = RiskScenarioTester()
        scenario_tester.run_all_scenarios()
        
        print("\n" + "="*60)
        print("PART 2: LIVE RISK TESTS")
        print("="*60)
        live_tester = LiveRiskTester()
        live_tester.run_preset_tests()
    
    elif choice == "4":
        print("\nGoodbye!")
    
    else:
        print("\nInvalid choice")


if __name__ == "__main__":
    main()