import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import time
import json

class TrafficFlowOptimizer:

    """
    Sistema inteligente de optimización de flujo vehicular para intersecciones semaforizadas.
    
    Utiliza algoritmos genéticos para determinar los tiempos óptimos de semáforos 
    basados en la demanda vehicular en tiempo real.
    
    Atributos:
        intersection (Intersection): Referencia a la intersección controlada
        flow_graph (nx.DiGraph): Grafo de flujo vehicular
        simulation_time_limit (int): Duración máxima de optimización (segundos)
        cycle_time (int): Duración total del ciclo semafórico (segundos)
        min_green_time (int): Tiempo mínimo de luz verde por dirección
        max_green_time (int): Tiempo máximo de luz verde por dirección
        vehicle_processing_rate (float): Capacidad de flujo (vehículos/segundo)
        metrics_history (dict): Registro histórico de métricas de desempeño
        optimization_active (bool): Estado del proceso de optimización
        current_optimal_times (dict): Mejor configuración encontrada
    """
    def __init__(self, intersection):
        """
        Inicializa el optimizador para una intersección específica.
        
        Args:
            intersection (Intersection): Objeto de intersección a optimizar.
            
        Configuración por defecto:
            - Ciclo semafórico: 120 segundos - Valor típico en ingeniería de tráfico para intersecciones medianas
            - Verde mínimo: 15 segundos - valor minimo de tiempo verde
            - Verde máximo: 60 segundos - valor maximo de tiempo verde
            - Tasa de procesamiento: 1.5 vehículos/segundo
        """
        self.intersection = intersection
        self.flow_graph = nx.DiGraph()
        self.simulation_time_limit = 300  # 5 minutos en segundos
        self.cycle_time = 120   # Ciclo completo de semáforos en segundos
        self.min_green_time = 15  # Tiempo mínimo de verde (aumentado)
        self.max_green_time = 60  # Tiempo máximo de verde
        
        # Parámetros de flujo vehicular
        self.vehicle_processing_rate = 1.5  # vehículos por segundo (más realista)
        self.yellow_time = 3  # tiempo amarillo fijo
        self.red_time = 2     # tiempo rojo fijo entre cambios
        
        # Métricas para análisis
        self.metrics_history = {
            'vehicles_passed': [],
            'waiting_times': [],
            'total_flow': [],
            'timestamp': []
        }
        
        # Estado de la optimización
        self.optimization_active = False
        self.optimization_start_time = 0
        self.current_optimal_times = None
        
    def start_optimization_cycle(self, time_limit_seconds=300):
        """
        Ejecuta un ciclo completo de optimización.
        
        Flujo del proceso:
        1. Valida la configuración actual
        2. Correge si es necesario
        3. Ejecuta algoritmo genético
        4. Aplica mejores tiempos encontrados
        
        Args:
            time_limit_seconds (int): Duración máxima del proceso
            
        Returns:
            dict: Tiempos óptimos por dirección {'N': int, 'S': int, 'E': int, 'W': int}
        """
        self.simulation_time_limit = time_limit_seconds
        self.optimization_active = True
        self.optimization_start_time = time.time()
        self.metrics_history = {key: [] for key in self.metrics_history.keys()}
        
        print(f"🚦 Iniciando optimización por {time_limit_seconds} segundos...")
        
        # Analizar estado inicial
        initial_state = self._analyze_current_state()
        print(f"📊 Estado inicial: {initial_state}")
        
        # Validar estado inicial
        if not self._validate_current_configuration():
            print("⚠️ Configuración inicial inválida, aplicando corrección...")
            self._fix_configuration()
        
        # Ejecutar optimización
        self.current_optimal_times = self.optimize_light_timing_genetic(generations=50)
        
        # Aplicar tiempos optimizados
        self._apply_optimized_times(self.current_optimal_times)
        
        print(f"✅ Tiempos optimizados aplicados: {self.current_optimal_times}")
        
        # Mostrar mejora esperada
        improvement = self._calculate_expected_improvement()
        print(f"📈 Mejora esperada: {improvement}")
        
        return self.current_optimal_times
    
    def _validate_current_configuration(self):
        """Valida que la configuración actual sea coherente"""
        current_times = self._get_current_light_times()
        total_time = sum(current_times.values())
        
        # Verificar que la suma sea correcta
        expected_total = self.cycle_time
        tolerance = 5  # margen de error
        
        if abs(total_time - expected_total) > tolerance:
            print(f"❌ Error: Tiempo total {total_time} != {expected_total}")
            return False
            
        # Verificar límites por dirección
        for direction, time in current_times.items():
            if time < self.min_green_time or time > self.max_green_time:
                print(f"❌ Error: Tiempo {direction} = {time} fuera de límites [{self.min_green_time}, {self.max_green_time}]")
                return False
                
        return True
    
    def _fix_configuration(self):
        """Corrige la configuración actual para que sea válida"""
        vehicle_counts = self._get_current_vehicle_counts()
        total_vehicles = sum(vehicle_counts.values())
        
        if total_vehicles == 0:
            # Sin vehículos: distribución uniforme
            time_per_direction = self.cycle_time // 4
            for direction in ['N', 'S', 'E', 'W']:
                self.intersection.change_light_times(direction, time_per_direction)
        else:
            # Con vehículos: distribución proporcional
            new_times = self._calculate_proportional_times(vehicle_counts)
            for direction, time in new_times.items():
                self.intersection.change_light_times(direction, time)
    
    def _calculate_proportional_times(self, vehicle_counts):
        """Calcula tiempos proporcionales a la demanda"""
        total_vehicles = sum(vehicle_counts.values())
        if total_vehicles == 0:
            return {d: self.cycle_time // 4 for d in ['N', 'S', 'E', 'W']}
        
        # Asignar tiempo mínimo primero
        times = {d: self.min_green_time for d in ['N', 'S', 'E', 'W']}
        remaining_time = self.cycle_time - 4 * self.min_green_time
        
        # Distribuir tiempo restante proporcionalmente
        for direction in ['N', 'S', 'E', 'W']:
            if remaining_time > 0:
                proportion = vehicle_counts[direction] / total_vehicles
                extra_time = int(remaining_time * proportion)
                times[direction] = min(self.max_green_time, 
                                     times[direction] + extra_time)
        
        # Ajustar para que sume exactamente cycle_time
        current_total = sum(times.values())
        if current_total != self.cycle_time:
            # Ajustar la diferencia en la dirección con más demanda
            max_demand_dir = max(vehicle_counts.keys(), 
                               key=lambda x: vehicle_counts[x])
            diff = self.cycle_time - current_total
            times[max_demand_dir] = max(self.min_green_time,
                                      min(self.max_green_time,
                                          times[max_demand_dir] + diff))
        
        return times
    
    def optimize_light_timing_genetic(self, generations=50, population_size=30):
        """ 
        Implementación de algoritmo genético para optimización semafórica.
        
        Parámetros del algoritmo:
            - Tasa de mutación: 20%
            - Tasa de cruce: 85%
            - Elitismo: 15%
            - Selección por torneo (size=3)
        
        Args:
            generations (int): Número máximo de generaciones
            population_size (int): Tamaño de la población
            
        Returns:
            dict: Mejor individuo encontrado
        
         """
        print(f"🧬 Iniciando algoritmo genético: {generations} generaciones, población {population_size}")
        
        mutation_rate = 0.20
        crossover_rate = 0.85
        elite_rate = 0.15
        
        # Generar población inicial
        population = self._generate_initial_population(population_size)
        
        best_fitness_history = []
        best_individual = None
        best_fitness = -float('inf')
        stagnation_counter = 0
        
        for generation in range(generations):
            # Evaluar fitness para toda la población
            fitness_scores = []
            for individual in population:
                fitness = self._evaluate_fitness_comprehensive(individual)
                fitness_scores.append((fitness, individual))
            
            # Ordenar por fitness (mayor es mejor)
            fitness_scores.sort(reverse=True, key=lambda x: x[0])
            current_best_fitness = fitness_scores[0][0]
            current_best_individual = fitness_scores[0][1]
            
            # Actualizar mejor global
            if current_best_fitness > best_fitness:
                best_fitness = current_best_fitness
                best_individual = current_best_individual.copy()
                stagnation_counter = 0
            else:
                stagnation_counter += 1
            
            best_fitness_history.append(current_best_fitness)
            
            # Mostrar progreso
            if generation % 10 == 0 or generation == generations - 1:
                avg_fitness = np.mean([score for score, _ in fitness_scores])
                print(f"Gen {generation:2d}: Mejor={current_best_fitness:.2f}, "
                      f"Promedio={avg_fitness:.2f}, Estancamiento={stagnation_counter}")
            
            # Condición de parada temprana
            if stagnation_counter > 15:
                print(f"🛑 Parada temprana en generación {generation} (estancamiento)")
                break
            
            # Crear nueva generación
            new_population = []
            elite_count = max(1, int(population_size * elite_rate))
            
            # Elitismo: conservar los mejores
            for i in range(elite_count):
                new_population.append(fitness_scores[i][1].copy())
            
            # Selección y reproducción
            while len(new_population) < population_size:
                if np.random.random() < crossover_rate and len(fitness_scores) >= 2:
                    # Selección por torneo
                    parent1 = self._tournament_selection(fitness_scores)
                    parent2 = self._tournament_selection(fitness_scores)
                    child = self._smart_crossover(parent1, parent2)
                else:
                    # Selección directa
                    child = self._tournament_selection(fitness_scores).copy()
                
                # Mutación
                if np.random.random() < mutation_rate:
                    child = self._adaptive_mutation(child)
                
                # Validar hijo
                if self._validate_individual(child):
                    new_population.append(child)
                else:
                    # Si no es válido, crear uno nuevo válido
                    new_population.append(self._create_valid_individual())
            
            population = new_population
        
        print(f"🎯 Optimización completada. Mejor fitness: {best_fitness:.2f}")
        return best_individual if best_individual else fitness_scores[0][1]
    
    def _evaluate_fitness_comprehensive(self, light_times):
        """
        Función de evaluación multicriterio para configuraciones semafóricas.
        
        Factores considerados:
        1. Throughput (vehículos procesados)
        2. Tiempo de espera estimado
        3. Balance del sistema
        4. Tiempo desperdiciado
        
        Cálculo:
        fitness = (throughput * 2.0) + (balance * 1.5) - 
                 (waiting_penalty * 1.0) - (waste_penalty * 0.5)
        
        Args:
            light_times (dict): Configuración a evaluar
            
        Returns:
            float: Valor de fitness (mayor es mejor)
        """
        # Validación básica
        if not self._validate_individual(light_times):
            return -1000  # Penalización severa para individuos inválidos
        
        vehicle_counts = self._get_current_vehicle_counts()
        total_fitness = 0
        
        # Factor 1: Throughput (vehículos procesados)
        throughput_score = 0
        total_vehicles_processed = 0
        
        for direction in ['N', 'S', 'E', 'W']:
            vehicles_waiting = vehicle_counts[direction]
            green_time = light_times[direction]
            
            # Vehículos que pueden procesarse en el tiempo verde
            max_processable = green_time * self.vehicle_processing_rate
            vehicles_processed = min(vehicles_waiting, max_processable)
            total_vehicles_processed += vehicles_processed
            
            # Score basado en eficiencia de procesamiento
            if vehicles_waiting > 0:
                efficiency = vehicles_processed / vehicles_waiting
                throughput_score += efficiency * vehicles_waiting
        
        # Factor 2: Tiempo de espera estimado
        waiting_time_penalty = 0
        for direction in ['N', 'S', 'E', 'W']:
            vehicles_waiting = vehicle_counts[direction]
            green_time = light_times[direction]
            
            if vehicles_waiting > 0:
                # Tiempo estimado para procesar todos los vehículos
                time_needed = vehicles_waiting / self.vehicle_processing_rate
                
                if time_needed > green_time:
                    # Algunos vehículos no podrán pasar en este ciclo
                    remaining_vehicles = vehicles_waiting - (green_time * self.vehicle_processing_rate)
                    # Penalización por tiempo de espera adicional
                    waiting_time_penalty += remaining_vehicles * (self.cycle_time / 60)  # normalizar
        
        # Factor 3: Balance del sistema
        balance_score = 0
        if sum(vehicle_counts.values()) > 0:
            # Penalizar configuraciones muy desbalanceadas cuando hay demanda desigual
            times_array = np.array(list(light_times.values()))
            demand_array = np.array(list(vehicle_counts.values()))
            
            # Normalizar demanda
            total_demand = sum(demand_array)
            if total_demand > 0:
                demand_ratio = demand_array / total_demand
                time_ratio = times_array / sum(times_array)
                
                # Calcular qué tan bien alineados están tiempo y demanda
                alignment = 1 - np.sum(np.abs(demand_ratio - time_ratio)) / 2
                balance_score = alignment * 10
        
        # Factor 4: Penalización por tiempo desperdiciado
        waste_penalty = 0
        for direction in ['N', 'S', 'E', 'W']:
            vehicles_waiting = vehicle_counts[direction]
            green_time = light_times[direction]
            
            # Tiempo mínimo necesario para procesar todos los vehículos
            min_time_needed = vehicles_waiting / self.vehicle_processing_rate
            
            # Si el tiempo verde es excesivo
            if green_time > min_time_needed + 5:  # 5 segundos de buffer
                excess_time = green_time - min_time_needed - 5
                waste_penalty += excess_time * 0.5
        
        # Cálculo final del fitness
        total_fitness = (throughput_score * 2.0 +  # Priorizar throughput
                        balance_score * 1.5 -      # Bonificar balance
                        waiting_time_penalty * 1.0 - # Penalizar espera
                        waste_penalty * 0.5)       # Penalizar desperdicio
        
        # Bonus por utilización completa
        utilization_rate = total_vehicles_processed / max(1, sum(vehicle_counts.values()))
        if utilization_rate > 0.9:
            total_fitness += 5  # Bonus por alta utilización
        
        return max(0, total_fitness)
    
    def _validate_individual(self, individual):
        """Valida que un individuo sea válido"""
        if not isinstance(individual, dict):
            return False
        
        required_directions = {'N', 'S', 'E', 'W'}
        if set(individual.keys()) != required_directions:
            return False
        
        # Verificar rangos
        for direction, time in individual.items():
            if not (self.min_green_time <= time <= self.max_green_time):
                return False
        
        # Verificar suma total
        total_time = sum(individual.values())
        if total_time != self.cycle_time:
            return False
            
        return True
    
    def _create_valid_individual(self):
        """Crea un individuo válido aleatoriamente"""
        vehicle_counts = self._get_current_vehicle_counts()
        return self._calculate_proportional_times(vehicle_counts)
    
    def _generate_initial_population(self, size):
        """Genera población inicial diversa y válida"""
        population = []
        vehicle_counts = self._get_current_vehicle_counts()
        
        for i in range(size):
            if i == 0:
                # Primera solución: proporcional a la demanda
                individual = self._calculate_proportional_times(vehicle_counts)
            elif i == 1:
                # Segunda solución: distribución uniforme
                time_per_direction = self.cycle_time // 4
                individual = {d: time_per_direction for d in ['N', 'S', 'E', 'W']}
            else:
                # Resto: variaciones aleatorias
                individual = {}
                remaining_time = self.cycle_time
                
                # Asignar tiempos aleatorios respetando restricciones
                directions = ['N', 'S', 'E', 'W']
                for i, direction in enumerate(directions):
                    if i == len(directions) - 1:
                        # Última dirección: asignar tiempo restante
                        individual[direction] = max(self.min_green_time,
                                                  min(self.max_green_time, remaining_time))
                    else:
                        # Otras direcciones: tiempo aleatorio
                        max_possible = min(self.max_green_time,
                                         remaining_time - (len(directions) - i - 1) * self.min_green_time)
                        min_possible = self.min_green_time
                        
                        if max_possible >= min_possible:
                            time = np.random.randint(min_possible, max_possible + 1)
                            individual[direction] = time
                            remaining_time -= time
                        else:
                            individual[direction] = self.min_green_time
                            remaining_time -= self.min_green_time
                
                # Validar y corregir si es necesario
                if not self._validate_individual(individual):
                    individual = self._calculate_proportional_times(vehicle_counts)
            
            population.append(individual)
        
        return population
    
    def _tournament_selection(self, fitness_scores, tournament_size=3):
        """Selección por torneo mejorada"""
        tournament_size = min(tournament_size, len(fitness_scores))
        tournament_indices = np.random.choice(len(fitness_scores), 
                                            tournament_size, 
                                            replace=False)
        
        # Seleccionar el mejor del torneo
        best_idx = min(tournament_indices)  # fitness_scores ya está ordenado
        return fitness_scores[best_idx][1]
    
    def _smart_crossover(self, parent1, parent2):
        """Crossover que mantiene la validez"""
        child = {}
        
        # Crossover uniforme
        for direction in ['N', 'S', 'E', 'W']:
            if np.random.random() < 0.5:
                child[direction] = parent1[direction]
            else:
                child[direction] = parent2[direction]
        
        # Corregir para que sea válido
        return self._make_individual_valid(child)
    
    def _adaptive_mutation(self, individual):
        """Mutación que mantiene la validez"""
        mutated = individual.copy()
        
        # Seleccionar dos direcciones para intercambiar tiempo
        directions = list(mutated.keys())
        dir1, dir2 = np.random.choice(directions, 2, replace=False)
        
        # Calcular cuánto tiempo se puede transferir
        max_transfer_from_dir1 = mutated[dir1] - self.min_green_time
        max_transfer_to_dir2 = self.max_green_time - mutated[dir2]
        
        max_transfer = min(max_transfer_from_dir1, max_transfer_to_dir2)
        
        if max_transfer > 0:
            # Transferir tiempo aleatorio
            transfer_amount = np.random.randint(1, min(max_transfer + 1, 10))
            mutated[dir1] -= transfer_amount
            mutated[dir2] += transfer_amount
        
        return mutated
    
    def _make_individual_valid(self, individual):
        """Hace válido un individuo inválido"""
        # Asegurar que todos los tiempos estén en rango
        for direction in individual:
            individual[direction] = max(self.min_green_time,
                                      min(self.max_green_time, individual[direction]))
        
        # Ajustar suma total
        current_total = sum(individual.values())
        target_total = self.cycle_time
        
        if current_total != target_total:
            diff = target_total - current_total
            
            # Distribuir la diferencia
            if diff > 0:
                # Necesitamos agregar tiempo
                directions = list(individual.keys())
                while diff > 0 and any(individual[d] < self.max_green_time for d in directions):
                    for direction in directions:
                        if diff > 0 and individual[direction] < self.max_green_time:
                            individual[direction] += 1
                            diff -= 1
            else:
                # Necesitamos quitar tiempo
                directions = list(individual.keys())
                while diff < 0 and any(individual[d] > self.min_green_time for d in directions):
                    for direction in directions:
                        if diff < 0 and individual[direction] > self.min_green_time:
                            individual[direction] -= 1
                            diff += 1
        
        return individual
    
    def _calculate_expected_improvement(self):
        """Calcula la mejora esperada con la nueva configuración"""
        if not self.current_optimal_times:
            return "No disponible"
        
        vehicle_counts = self._get_current_vehicle_counts()
        current_times = self._get_current_light_times()
        
        # Calcular throughput actual vs optimizado
        current_throughput = 0
        optimal_throughput = 0
        
        for direction in ['N', 'S', 'E', 'W']:
            vehicles = vehicle_counts[direction]
            
            # Throughput actual
            current_processable = min(vehicles, 
                                    current_times[direction] * self.vehicle_processing_rate)
            current_throughput += current_processable
            
            # Throughput optimizado
            optimal_processable = min(vehicles,
                                    self.current_optimal_times[direction] * self.vehicle_processing_rate)
            optimal_throughput += optimal_processable
        
        if current_throughput > 0:
            improvement_percent = ((optimal_throughput - current_throughput) / current_throughput) * 100
            return f"{improvement_percent:.1f}% más vehículos procesados por ciclo"
        else:
            return "No hay vehículos para procesar"
    
    # Métodos auxiliares que ya tenías (mantengo los existentes)
    def _get_current_vehicle_counts(self):
        """Obtiene conteo actual de vehículos"""
        counts = {}
        for direction in ['N', 'S', 'E', 'W']:
            counts[direction] = len(self.intersection.vehicles[direction])
        return counts
    
    def _get_current_light_times(self):
        """Obtiene tiempos actuales de semáforos"""
        times = {}
        for direction in ['N', 'S', 'E', 'W']:
            times[direction] = self.intersection.traffic_lights[direction].green_time
        return times
    
    def _apply_optimized_times(self, optimal_times):
        """Aplica los tiempos optimizados a la intersección"""
        for direction, time in optimal_times.items():
            self.intersection.change_light_times(direction, time)
    
    def _analyze_current_state(self):
        """Analiza el estado actual del sistema"""
        vehicle_counts = self._get_current_vehicle_counts()
        light_times = self._get_current_light_times()
        
        return {
            'vehicles_waiting': vehicle_counts,
            'current_light_times': light_times,
            'total_vehicles': sum(vehicle_counts.values()),
            'total_green_time': sum(light_times.values())
        }
    
    def debug_optimization_state(self):
        """Método para verificar el estado de la optimización"""
        vehicle_counts = self._get_current_vehicle_counts()
        current_times = self._get_current_light_times()
        
        print("\n🔍 DEBUG - Estado de optimización:")
        print(f"Vehículos por dirección: {vehicle_counts}")
        print(f"Tiempos actuales: {current_times}")
        print(f"Suma tiempos: {sum(current_times.values())}")
        print(f"Cycle time configurado: {self.cycle_time}")
        print(f"Configuración válida: {self._validate_current_configuration()}")
        
        # Calcular distribución óptima teórica
        total_vehicles = sum(vehicle_counts.values())
        if total_vehicles > 0:
            print("\n📊 Distribución teórica óptima:")
            optimal_times = self._calculate_proportional_times(vehicle_counts)
            for direction in ['N', 'S', 'E', 'W']:
                print(f"  {direction}: {optimal_times[direction]}s (vehículos: {vehicle_counts[direction]})")
