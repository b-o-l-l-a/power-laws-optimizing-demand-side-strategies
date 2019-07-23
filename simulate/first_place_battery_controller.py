from ortools.linear_solver import pywraplp

class BatteryController(object):
    """ The BatteryContoller class handles providing a new "target state of charge"
        at each time step.
        This class is instantiated by the simulation script, and it can
        be used to store any state that is needed for the call to
        propose_state_of_charge that happens in the simulation.
        The propose_state_of_charge method returns the state of
        charge between 0.0 and 1.0 to be attained at the end of the coming
        quarter, i.e., at time t+15 minutes.
        The arguments to propose_state_of_charge are as follows:
        :param site_id: The current site (building) id in case the model does different work per site
        :param timestamp: The current timestamp inlcuding time of day and date
        :param battery: The battery (see battery.py for useful properties, including current_charge and capacity)
        :param actual_previous_load: The actual load of the previous quarter.
        :param actual_previous_pv_production: The actual PV production of the previous quarter.
        :param price_buy: The price at which electricity can be bought from the grid for the
          next 96 quarters (i.e., an array of 96 values).
        :param price_sell: The price at which electricity can be sold to the grid for the
          next 96 quarters (i.e., an array of 96 values).
        :param load_forecast: The forecast of the load (consumption) established at time t for the next 96
          quarters (i.e., an array of 96 values).
        :param pv_forecast: The forecast of the PV production established at time t for the next
          96 quarters (i.e., an array of 96 values).
        :returns: proposed state of charge, a float between 0 (empty) and 1 (full).
    """
    
    step = 960
    
    def propose_state_of_charge(self,
                                site_id,
                                timestamp,
                                battery,
                                actual_previous_load,
                                actual_previous_pv_production,
                                price_buy,
                                price_sell,
                                load_forecast,
                                pv_forecast):

        # return the proposed state of charge ...
        
# Step 1: Create the variables.
######## current_charge
######## expected load in next 15 mins
######## expected pv to add to charge in next 15 mins
######## price to buy energy if PV + Storage < Load
######## price to sell energy if PV + Storage > Load, and 
# Step 2: Define the constraints.
# Step 3: Define the objective function.
# Step 4: Declare the solver—the method that implements an algorithm for finding the optimal solution.
# Step 5: Invoke the solver and display the results.     

        # divide by 4 bc power_limit is based on hour, timestep @ 15 mins
#         timestep_max_charge = (battery.charging_power_limit * battery.charging_efficiency) / 4.
#         timestep_max_discharge = (battery.discharging_power_limit * battery.discharging_efficiency) / 4.
        
#         grid_energy = actual_previous_load - actual_previous_pv_production
        
#         current_grid_buy_price = price_buy[0]
#         print("---------\n")
#         print("price_buy[0]", price_buy[0])
#         print("price_sell[0]", price_sell[0])
#         grid_sell_price = price_sell[0] if len(price_sell.unique()) == 0 else None #raise ValueError('more than one sell price')
        
#         max_grid_buy_price = max(price_buy)        
#         min_grid_buy_price = min(price_buy)


######### WINNING SOLUTION - START
        self.step -= 1
        if (self.step == 0): return 0
        else: 
            number_step = min(96, abs(self.step))
            
        #
        print(timestamp, self.step)
        print("actual_previous_load", actual_previous_load)
        print("actual_previous_pv_production", actual_previous_pv_production)
        
        price_buy = price_buy.tolist()
        price_sell = price_sell.tolist()
        load_forecast = load_forecast.tolist()
        pv_forecast = pv_forecast.tolist() 
        
        # energy: amount of surplus/deficit energy at a specific timestep, depending on actual load / pv values
        energy = [None] * number_step

        for i in range(number_step):
            if (pv_forecast[i] >=50): energy[i] = load_forecast[i] - pv_forecast[i]
            else: energy[i] = load_forecast[i]

        capacity = battery.capacity
        charging_efficiency = battery.charging_efficiency
        discharging_efficiency = 1. / battery.discharging_efficiency
        current = capacity * battery.current_charge 
        limit = battery.charging_power_limit
        dis_limit = battery.discharging_power_limit
        limit /= 4.
        dis_limit /= 4.

        # Ortools
        solver = pywraplp.Solver("B", pywraplp.Solver.GLOP_LINEAR_PROGRAMMING)
         
        #Variables: all are continous
        # charge: how much PV to use to charge battery at given time step
        charge = [solver.NumVar(0.0, limit, "c"+str(i)) for i in range(number_step)] 
        # dis_charge: how much energy from battery to use meet load restrictions
        dis_charge = [solver.NumVar( dis_limit, 0.0, "d"+str(i)) for i in range(number_step)]
        # battery_power: amount of power a battery has for each timestep
        battery_power = [solver.NumVar(0.0, capacity, "b"+str(i)) for i in range(number_step+1)]
        # grid: amount of energy to get from grid at each timestep
        grid = [solver.NumVar(0.0, solver.infinity(), "g"+str(i)) for i in range(number_step)] 
        
        #Objective function
        objective = solver.Objective()
        for i in range(number_step):
            objective.SetCoefficient(grid[i], price_buy[i] - price_sell[i]) # why is the coefficient the difference bt buy and sell price?
            objective.SetCoefficient(charge[i], price_sell[i] + price_buy[i] / 1000.) # why is the coefficient the sum of buy and sell price?
            objective.SetCoefficient(dis_charge[i], price_sell[i])             
        objective.SetMinimization()
         
        # 3 Constraints
        c_grid = [None] * number_step
        c_power = [None] * (number_step+1)
         
        # first constraint
        c_power[0] = solver.Constraint(current, current)
        c_power[0].SetCoefficient(battery_power[0], 1)
         
        for i in range(0, number_step):
            # second constraint
            c_grid[i] = solver.Constraint(energy[i], solver.infinity())
            c_grid[i].SetCoefficient(grid[i], 1)
            c_grid[i].SetCoefficient(charge[i], -1)
            c_grid[i].SetCoefficient(dis_charge[i], -1)
            # third constraint
            c_power[i+1] = solver.Constraint( 0, 0)
            c_power[i+1].SetCoefficient(charge[i], charging_efficiency)
            c_power[i+1].SetCoefficient(dis_charge[i], discharging_efficiency)
            c_power[i+1].SetCoefficient(battery_power[i], 1)
            c_power[i+1].SetCoefficient(battery_power[i+1], -1)

        #solve the model
        solver.Solve()
        print("grid[0]", grid[0].solution_value())
        print("charge[0]", charge[0].solution_value())
        print("dis_charge[0]", dis_charge[0].solution_value())
        
#         print("energy[0]", energy[0])
#         print("charge[0].solution_value()", charge[0].solution_value())
        print("\n\n\n")
#         print(grid[0].solution_value())
#         print("\n\n\n")
        if ((energy[0] < 0) & (dis_charge[0].solution_value() >= 0)):

            n = 0
            first = -limit
            mid = 0

            sum_charge = charge[0].solution_value()
            last = energy[0]
            for n in range(1, number_step):
                if((energy[n] > 0) | (dis_charge[n].solution_value() < 0) | (price_sell[n] != price_sell[n-1])):
                    break
                last = min(last, energy[n])
                sum_charge += charge[n].solution_value()
            if (sum_charge <= 0.):
                 return battery_power[1].solution_value() / capacity
            def tinh(X):
                res = 0
                for i in range(n):
                    res += min(limit, max(-X - energy[i], 0.))
                if (res >= sum_charge): return True
                return False 
            last = 2 - last
            # binary search
            while (last - first > 1):
                mid = (first + last) / 2
                if (tinh(mid)): first = mid
                else: last = mid
            #print("(current + min(limit, max(-first - energy[0] , 0)) * charging_efficiency) / capacity")
            #print((current + min(limit, max(-first - energy[0] , 0)) * charging_efficiency) / capacity)
            return (current + min(limit, max(-first - energy[0] , 0)) * charging_efficiency) / capacity
        
        if ((energy[0] > 0) & (charge[0].solution_value() <=0)):
   
            n = 0
            first = dis_limit
            mid = 0
            sum_discharge = dis_charge[0].solution_value()
            last = energy[0]
            for n in range(1, number_step):
                if ((energy[n] < 0) | (charge[n].solution_value() > 0) | (price_sell[n] != price_sell[n-1]) | (price_buy[n] != price_buy[n-1])):
                    break
                last = max(last, energy[n])
                sum_discharge += dis_charge[n].solution_value()
            if (sum_discharge >= 0.): 
                #print("battery_power[1].solution_value() / capacity", battery_power[1].solution_value() / capacity)
                return battery_power[1].solution_value() / capacity

            def tinh2(X):
                res = 0
                for i in range(n):
                    res += max(dis_limit, min(X - energy[i], 0))
                if (res <= sum_discharge): return True
                return False                      
            last += 2

            # binary search
            while (last - first > 1):
                mid = (first + last) / 2
                if (tinh2(mid)): first = mid
                else: last = mid
            
            #print("(current +  max(dis_limit, min(first - energy[0], 0)) * discharging_efficiency) / capacity")
            #print((current +  max(dis_limit, min(first - energy[0], 0)) * discharging_efficiency) / capacity)
            return (current +  max(dis_limit, min(first - energy[0], 0)) * discharging_efficiency) / capacity
        
        return battery_power[1].solution_value() / capacity