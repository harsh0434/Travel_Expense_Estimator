def get_indian_destinations():
    """Return a list of Indian destinations with their regions"""
    return {
        # North India
        'delhi': 'north india',
        'agra': 'north india',
        'jaipur': 'north india',
        'varanasi': 'north india',
        'amritsar': 'north india',
        'shimla': 'north india',
        'manali': 'north india',
        'ladakh': 'north india',
        'rishikesh': 'north india',
        'haridwar': 'north india',
        
        # South India
        'bangalore': 'south india',
        'mysore': 'south india',
        'ooty': 'south india',
        'chennai': 'south india',
        'pondicherry': 'south india',
        'hyderabad': 'south india',
        'hampi': 'south india',
        'kerala backwaters': 'south india',
        'munnar': 'south india',
        'kovalam': 'south india',
        
        # East India
        'kolkata': 'east india',
        'darjeeling': 'east india',
        'gangtok': 'east india',
        'puri': 'east india',
        'sundarbans': 'east india',
        'shillong': 'east india',
        'kaziranga': 'east india',
        'tawang': 'east india',
        'bodhgaya': 'east india',
        'majuli': 'east india',
        
        # West India
        'mumbai': 'west india',
        'goa': 'west india',
        'udaipur': 'west india',
        'jodhpur': 'west india',
        'jaisalmer': 'west india',
        'mount abu': 'west india',
        'kutch': 'west india',
        'ajanta & ellora caves': 'west india',
        'dwarka': 'west india',
        'diu': 'west india',
        
        # Central India
        'khajuraho': 'central india',
        'orchha': 'central india',
        'sanchi': 'central india',
        'bhopal': 'central india',
        'pachmarhi': 'central india',
        'kanha': 'central india',
        'bandhavgarh': 'central india',
        'gwalior': 'central india',
        'mandu': 'central india',
        'bhimbetka': 'central india'
    }

def calculate_travel_cost(days, people, travel_mode, budget, region):
    """Calculate travel cost based on input parameters"""
    # Base costs per person per day for different budget levels (in INR)
    base_costs = {
        'low': {
            'accommodation': 1000,    # Basic hotel/hostel
            'food': 500,              # Basic meals
            'activities': 300,        # Basic sightseeing
            'transport': 500          # Local transport
        },
        'mid': {
            'accommodation': 2500,    # Mid-range hotel
            'food': 1000,             # Mid-range restaurants
            'activities': 800,        # Guided tours
            'transport': 1000         # Comfortable transport
        },
        'high': {
            'accommodation': 5000,    # Luxury hotel
            'food': 2000,             # Fine dining
            'activities': 1500,       # Premium activities
            'transport': 2000         # Private transport
        }
    }
    
    # Region multipliers for Indian regions
    region_multipliers = {
        'north india': 1.1,  # Higher due to tourist popularity and extreme weather conditions
        'south india': 0.9,  # Moderate costs
        'east india': 0.8,   # Generally lower costs
        'west india': 1.2,   # Higher due to tourist destinations and business centers
        'central india': 0.7 # Lower costs due to less tourist traffic
    }
    
    # Travel mode multipliers
    mode_multipliers = {
        'car': 0.8,
        'bus': 0.6,
        'train': 1.0,
        'airways': 1.5
    }
    
    # Get base costs for selected budget
    daily_costs = base_costs[budget].copy()
    
    # Apply region multiplier
    region_mult = region_multipliers[region]
    for cost_type in daily_costs:
        daily_costs[cost_type] *= region_mult
    
    # Apply travel mode multiplier to transport cost only
    daily_costs['transport'] *= mode_multipliers[travel_mode]
    
    # Calculate total daily cost per person
    total_daily_cost = sum(daily_costs.values())
    
    # Calculate total cost for all people and days
    total_cost = total_daily_cost * days * people
    
    return {
        'total_cost': total_cost,
        'daily_costs': daily_costs
    }

def main():
    """Main function to get user input and show results"""
    print("Indian Travel Expense Estimator")
    print("--------------------")
    
    # Get destination
    indian_destinations = get_indian_destinations()
    print("\nAvailable destinations in India:")
    destinations = sorted(indian_destinations.keys())
    for idx, dest in enumerate(destinations, 1):
        print(f"{idx}. {dest.title()}")
    
    while True:
        dest_input = input("\nEnter destination name or number: ").lower().strip()
        try:
            # Try to convert input to number
            dest_idx = int(dest_input) - 1
            if 0 <= dest_idx < len(destinations):
                destination = destinations[dest_idx]
                break
        except ValueError:
            # If not a number, check if it's a valid destination name
            if dest_input in indian_destinations:
                destination = dest_input
                break
        print("Invalid destination. Please enter a valid destination name or number.")
    
    # Get number of days
    while True:
        try:
            days = int(input("\nEnter number of days (1-30): "))
            if 1 <= days <= 30:
                break
            print("Please enter a number between 1 and 30.")
        except ValueError:
            print("Please enter a valid number.")
    
    # Get number of people
    while True:
        try:
            people = int(input("Enter number of people (1-10): "))
            if 1 <= people <= 10:
                break
            print("Please enter a number between 1 and 10.")
        except ValueError:
            print("Please enter a valid number.")
    
    # Get travel mode
    print("\nTravel modes available:")
    print("1. car")
    print("2. bus")
    print("3. train")
    print("4. airways")
    
    mode_map = {
        '1': 'car', 
        '2': 'bus', 
        '3': 'train', 
        '4': 'airways',
        'car': 'car',
        'bus': 'bus',
        'train': 'train',
        'airways': 'airways'
    }
    
    while True:
        mode_input = input("Enter travel mode (1-4 or name): ").lower().strip()
        if mode_input in mode_map:
            travel_mode = mode_map[mode_input]
            break
        print("Error: Invalid travel mode. Please enter 1-4 or the mode name (car, bus, train, airways)")
    
    # Get budget level
    print("\nBudget levels available:")
    print("1. low (Basic accommodation and meals)")
    print("2. mid (Comfortable hotels and restaurants)")
    print("3. high (Luxury hotels and fine dining)")
    
    budget_map = {'1': 'low', '2': 'mid', '3': 'high'}
    while True:
        budget = input("Enter budget level (1-3 or name): ").lower().strip()
        if budget in budget_map:
            budget = budget_map[budget]
        if budget in ['low', 'mid', 'high']:
            break
        print("Error: Invalid budget level. Please enter 1-3 or the level name (low, mid, high)")
    
    # Get region for the selected destination
    region = indian_destinations[destination]
    
    # Calculate costs
    result = calculate_travel_cost(days, people, travel_mode, budget, region)
    
    # Calculate per-person and per-day costs
    per_person_cost = result['total_cost'] / people
    per_day_cost = result['total_cost'] / days
    per_day_per_person_cost = per_person_cost / days
    
    print("\nEstimated Travel Costs:")
    print("----------------------")
    print(f"Destination: {destination.title()}")
    print(f"Total Cost: ₹{result['total_cost']:,.2f}")
    print(f"Cost per person: ₹{per_person_cost:,.2f}")
    print(f"Cost per day: ₹{per_day_cost:,.2f}")
    print(f"Cost per day per person: ₹{per_day_per_person_cost:,.2f}")
    
    print("\nDaily Cost Breakdown (including regional adjustment):")
    print(f"Accommodation: ₹{result['daily_costs']['accommodation']:,.2f}")
    print(f"Food: ₹{result['daily_costs']['food']:,.2f}")
    print(f"Activities: ₹{result['daily_costs']['activities']:,.2f}")
    print(f"Transportation: ₹{result['daily_costs']['transport']:,.2f}")
    
    # Show transportation cost based on mode
    print("\nTransportation Details:")
    if travel_mode == 'car':
        print("Estimated fuel cost included in transportation")
    elif travel_mode == 'bus':
        print("Bus tickets included in transportation")
    elif travel_mode == 'train':
        print("Train tickets included in transportation")
    else:  # airways
        print("Air tickets included in transportation")

if __name__ == "__main__":
    main() 