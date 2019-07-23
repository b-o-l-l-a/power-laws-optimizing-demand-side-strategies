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
        
        # return the proposed state of charge ...

        self.step -= 1
        if (self.step == 1): return 0
        if (self.step > 1): number_step = min(96, self.step)
            
        print(timestamp, self.step)
        print("actual_previous_load", actual_previous_load)
        print("actual_previous_pv_production", actual_previous_pv_production)

        price_buy = price_buy.tolist()
        price_sell = price_sell.tolist()
        load_forecast = load_forecast.tolist()
        pv_forecast = pv_forecast.tolist() 

        #battery
#         print("battery.capacity", battery.capacity)
#         print("battery.charging_efficiency", battery.charging_efficiency)
#         print("battery.discharging_efficiency", battery.discharging_efficiency)
#         print("1. / battery.discharging_efficiency", 1. / battery.discharging_efficiency)
#         print("(current) capacity * battery.current_charge", battery.capacity * battery.current_charge)
#         print("battery.charging_power_limit", battery.charging_power_limit)
#         print("battery.discharging_power_limit", battery.discharging_power_limit)
#         print("battery.current_charge", battery.current_charge)       
        
        battery_capacity = battery.capacity
        charging_efficiency = battery.charging_efficiency
        discharging_efficiency = battery.discharging_efficiency
        current = battery_capacity * battery.current_charge 
        print("current", current)
        charge_limit = battery.charging_power_limit
        discharge_limit = battery.discharging_power_limit
        charge_limit /= 4.
        discharge_limit /= 4.


        # Ortools
        solver = pywraplp.Solver("BatteryCharge", pywraplp.Solver.GLOP_LINEAR_PROGRAMMING)
         
        # charge: how much PV to use to charge battery at given time step
        charge = [solver.NumVar(0.0, charge_limit, "charge_{}".format(i)) for i in range(number_step)] 
        
        # discharge: how much energy from battery to use meet load restrictions
        discharge = [solver.NumVar( discharge_limit, 0.0, "discharge_{}".format(i)) for i in range(number_step)]
        
        # battery_power: amount of power a battery has for each timestep
        battery_power = [solver.NumVar(0.0, battery_capacity, "battery_charge_{}".format(i)) for i in range(number_step + 1)]
        
        # grid_energy: amount of energy to get from grid at each timestep
        grid_energy = [solver.NumVar(0.0, solver.infinity(), "grid_{}".format(i)) for i in range(number_step)] 
        
        # energy_reqd: amount of surplus/deficit energy at a specific timestep, depending on actual load / pv values
        energy_reqd = [None] * number_step

        for i in range(number_step):
            energy_reqd[i] = load_forecast[i] - pv_forecast[i]
            
        #energy_to_buy = [solver.NumVar(0.0, solver.infinity(), "energy_to_buy_{}".format(i)) for i in range(number_step)] 
        energy_to_sell = [solver.NumVar(discharge_limit, 0, "energy_to_sell_{}".format(i)) for i in range(number_step)]
        
        #Objective function
        objective = solver.Objective()

        for i in range(number_step):
            objective.SetCoefficient(grid_energy[i], price_buy[i] - price_sell[i])
            objective.SetCoefficient(charge[i], price_buy[i])
            objective.SetCoefficient(discharge[i], -price_sell[i])
      
        objective.SetMinimization()
        
        grid_constraint = [None] * number_step
        battery_constraint = [None] * (number_step + 1)
        battery_constraint[0] = solver.Constraint(current, current)
        battery_constraint[0].SetCoefficient(battery_power[0], 1)
        
        for i in range(0, number_step):
            
            grid_constraint[i] = solver.Constraint(energy_reqd[i], solver.infinity())
            grid_constraint[i].SetCoefficient(grid_energy[i], 1)
            ##grid_constraint[i].SetCoefficient(energy_to_sell[i], -1)
            grid_constraint[i].SetCoefficient(charge[i], -1)
            grid_constraint[i].SetCoefficient(discharge[i], -1)
            
            battery_constraint[i + 1] = solver.Constraint(0, 0)
            battery_constraint[i + 1].SetCoefficient(charge[i], charging_efficiency)
            battery_constraint[i + 1].SetCoefficient(discharge[i], discharging_efficiency)
            #battery_constraint[i + 1].SetCoefficient(energy_to_sell[i], discharging_efficiency)
            battery_constraint[i + 1].SetCoefficient(battery_power[i], 1)
            battery_constraint[i + 1].SetCoefficient(battery_power[i + 1], -1)

        solver.Solve()
        
        print("grid_energy[0]", grid_energy[0].solution_value())
        print("charge[0]", charge[0].solution_value())
        if charge[0].solution_value() > 0:
            raise ValueError('Charge is above 0')
        print("discharge[0]", discharge[0].solution_value())
        print("battery_power[i]", battery_power[i].solution_value())
        print("battery_power[i + 1]", battery_power[i + 1].solution_value())
        print("\n\n\n")

        return 0.5
