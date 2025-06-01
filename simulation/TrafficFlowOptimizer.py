# traffic_optimizer.py
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple
import time
import json
from collections import defaultdict

class TrafficFlowOptimizer:
    def __init__(self, intersection):
        self.intersection = intersection
        self.flow_graph = nx.DiGraph()
        self.simulation_time_limit = 300  # 5 minutos en segundos (ajustable)
        self.cycle_time = 120   # Ciclo completo de semáforos en segundos
        self.min_green_time = 10  # Tiempo mínimo de verde
        self.max_green_time = 50  # Tiempo máximo de verde
        
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
        Inicia un ciclo de optimización con tiempo límite
        """
        self.simulation_time_limit = time_limit_seconds
        self.optimization_active = True
        self.optimization_start_time = time.time()
        self.metrics_history = {key: [] for key in self.metrics_history.keys()}
        
        print(f"🚦 Iniciando optimización por {time_limit_seconds} segundos...")
        
        # Analizar estado inicial
        initial_state = self._analyze_current_state()
        print(f"📊 Estado inicial: {initial_state}")
        
        # Ejecutar optimización
        self.current_optimal_times = self.optimize_light_timing_genetic(generations=30)
        
        # Aplicar tiempos optimizados
        self._apply_optimized_times(self.current_optimal_times)
        
        print(f"✅ Tiempos optimizados aplicados: {self.current_optimal_times}")
        
        return self.current_optimal_times
    
    def update_optimization_metrics(self, toggle_timer):
        """
        Actualiza métricas durante la simulación (llamar desde el loop principal)
        """
        if not self.optimization_active:
            return
            
        current_time = time.time()
        elapsed_time = current_time - self.optimization_start_time
        
        # Recopilar métricas actuales
        vehicles_passed = self._count_total_vehicles_passed()
        avg_waiting_time = self._calculate_average_waiting_time()
        total_flow = self._calculate_current_flow_rate()
        
        # Guardar métricas
        self.metrics_history['vehicles_passed'].append(vehicles_passed)
        self.metrics_history['waiting_times'].append(avg_waiting_time)
        self.metrics_history['total_flow'].append(total_flow)
        self.metrics_history['timestamp'].append(elapsed_time)
        
        # Verificar si se acabó el tiempo
        if elapsed_time >= self.simulation_time_limit:
            self._finalize_optimization()
    
    def _finalize_optimization(self):
        """
        Finaliza el ciclo de optimización y genera reporte
        """
        self.optimization_active = False
        final_report = self._generate_optimization_report()
        
        print("\n" + "="*50)
        print("🎯 REPORTE FINAL DE OPTIMIZACIÓN")
        print("="*50)
        print(final_report)
        
        # Guardar resultados en archivo
        self._save_results_to_file()
        
        # Generar gráficos
        self._plot_optimization_results()
        
        return final_report
    
    def build_flow_network(self):
        """
        Construye el grafo de flujo que representa la intersección
        """
        self.flow_graph.clear()
        
        # Nodos del grafo
        directions = ['N', 'S', 'E', 'W']
        
        # Fuentes (donde llegan los vehículos)
        sources = [f'source_{d}' for d in directions]
        
        # Nodo central de la intersección
        intersection_node = 'intersection'
        
        # Sumideros (donde salen los vehículos)
        sinks = [f'sink_{d}' for d in directions]
        
        # Agregar nodos
        self.flow_graph.add_nodes_from(sources + [intersection_node] + sinks)
        
        # Obtener datos actuales
        vehicle_counts = self._get_current_vehicle_counts()
        light_times = self._get_current_light_times()
        
        # Crear aristas con capacidades
        for direction in directions:
            source = f'source_{direction}'
            sink = f'sink_{direction}'
            
            # Capacidad de entrada (vehículos esperando -> intersección)
            input_capacity = self._calculate_input_capacity(direction, vehicle_counts, light_times)
            self.flow_graph.add_edge(source, intersection_node, 
                                   capacity=input_capacity, 
                                   direction=direction,
                                   type='input')
            
            # Capacidad de salida (intersección -> destinos)
            output_capacity = self._calculate_output_capacity(direction, light_times)
            self.flow_graph.add_edge(intersection_node, sink, 
                                   capacity=output_capacity, 
                                   direction=direction,
                                   type='output')
        
        return self.flow_graph
    
    def optimize_light_timing_genetic(self, generations=50, population_size=20):
        """
        Algoritmo genético optimizado para el sistema
        """
        mutation_rate = 0.15
        crossover_rate = 0.8
        
        # Generar población inicial
        population = self._generate_initial_population(population_size)
        
        best_fitness_history = []
        
        for generation in range(generations):
            # Evaluar fitness
            fitness_scores = []
            for individual in population:
                fitness = self._evaluate_fitness_comprehensive(individual)
                fitness_scores.append((fitness, individual))
            
            # Ordenar por fitness
            fitness_scores.sort(reverse=True, key=lambda x: x[0])
            best_fitness_history.append(fitness_scores[0][0])
            
            # Selección por torneo
            selected = self._tournament_selection(fitness_scores, population_size // 2)
            
            # Crear nueva generación
            new_population = []
            
            # Elitismo: mantener los mejores
            elite_count = max(1, population_size // 10)
            new_population.extend([ind for _, ind in fitness_scores[:elite_count]])
            
            # Crossover y mutación
            while len(new_population) < population_size:
                if np.random.random() < crossover_rate:
                    parent1, parent2 = np.random.choice(selected, 2, replace=False)
                    child = self._smart_crossover(parent1, parent2)
                else:
                    child = np.random.choice(selected).copy()
                
                if np.random.random() < mutation_rate:
                    child = self._adaptive_mutation(child)
                
                new_population.append(child)
            
            population = new_population
            
            # Mostrar progreso cada 10 generaciones
            if generation % 10 == 0:
                print(f"Generación {generation}: Mejor fitness = {fitness_scores[0][0]:.2f}")
        
        best_solution = fitness_scores[0][1]
        return best_solution
    
    def _generate_initial_population(self, size):
        """Genera población inicial con restricciones correctas"""
        population = []
        
        # Obtener configuración actual como base
        vehicle_counts = self._get_current_vehicle_counts()
        total_vehicles = sum(vehicle_counts.values())
        
        for _ in range(size):
            individual = {}
            
            if total_vehicles > 0:
                # Calcular proporción basada en demanda
                remaining_time = self.cycle_time
                
                # Asignar tiempo mínimo a todas las direcciones primero
                for direction in ['N', 'S', 'E', 'W']:
                    individual[direction] = self.min_green_time
                    remaining_time -= self.min_green_time
                
                # Distribuir tiempo restante proporcionalmente
                for direction in ['N', 'S', 'E', 'W']:
                    if remaining_time > 0:
                        demand_ratio = vehicle_counts[direction] / total_vehicles
                        extra_time = int(remaining_time * demand_ratio)
                        
                        # Agregar variación aleatoria pequeña
                        variation = np.random.randint(-3, 4)
                        extra_time = max(0, extra_time + variation)
                        
                        # Verificar que no exceda máximo
                        individual[direction] = min(
                            individual[direction] + extra_time,
                            self.max_green_time
                        )
                
                # VALIDACIÓN CRÍTICA: Ajustar para que sume exactamente cycle_time
                current_total = sum(individual.values())
                if current_total != self.cycle_time:
                    # Ajustar proporcionalmente
                    factor = self.cycle_time / current_total
                    for direction in individual:
                        individual[direction] = max(
                            self.min_green_time,
                            min(self.max_green_time, int(individual[direction] * factor))
                        )
                    
                    # Ajuste fino para que sume exactamente
                    current_total = sum(individual.values())
                    diff = self.cycle_time - current_total
                    
                    if diff != 0:
                        # Ajustar la dirección con más demanda
                        max_demand_dir = max(vehicle_counts.keys(), 
                                        key=lambda x: vehicle_counts[x])
                        individual[max_demand_dir] = max(
                            self.min_green_time,
                            min(self.max_green_time, individual[max_demand_dir] + diff)
                        )
            else:
                # Sin vehículos: distribución uniforme
                time_per_direction = self.cycle_time // 4
                for direction in ['N', 'S', 'E', 'W']:
                    individual[direction] = time_per_direction
            
            # Verificación final
            assert sum(individual.values()) == self.cycle_time, f"Error: suma={sum(individual.values())}, esperado={self.cycle_time}"
            
            population.append(individual)
        
        return population
    
    def _evaluate_fitness_comprehensive(self, light_times):
        """
        Función de fitness mejorada que considera múltiples factores
        """
            # VALIDAR que suma sea correcta
        if sum(light_times.values()) != self.cycle_time:
            return 0  # Fitness cero para soluciones inválidas
        
        vehicle_counts = self._get_current_vehicle_counts()
        total_fitness = 0
        
        # Factor 1: Eficiencia de procesamiento por dirección
        for direction in ['N', 'S', 'E', 'W']:
            vehicles = vehicle_counts[direction]
            green_time = light_times[direction]
            
            if vehicles > 0:
                # Vehículos que pueden procesarse (2 veh/seg)
                vehicles_processed = min(vehicles, green_time * 2.0)
                
                # Eficiencia: porcentaje de vehículos procesados
                efficiency = vehicles_processed / vehicles
                total_fitness += efficiency * vehicles  # Ponderado por cantidad
        
        # Factor 2: Penalizar tiempo desperdiciado
        for direction in ['N', 'S', 'E', 'W']:
            vehicles = vehicle_counts[direction]
            green_time = light_times[direction]
            
            # Si el tiempo verde es excesivo para los vehículos presentes
            max_needed_time = vehicles / 2.0  # Tiempo máximo necesario
            if green_time > max_needed_time + 5:  # +5 segundos de buffer
                waste_penalty = (green_time - max_needed_time - 5) * 0.1
                total_fitness -= waste_penalty
        
        # Factor 3: Balance (evitar extremos)
        times = list(light_times.values())
        balance_bonus = 10 / (1 + np.std(times))  # Bonus por balance
        
        return max(0, total_fitness + balance_bonus)
    
    def _build_temp_flow_graph(self, light_times):
        """Construye grafo temporal para evaluación"""
        temp_graph = nx.DiGraph()
        
        # Agregar nodos y aristas como en build_flow_network
        directions = ['N', 'S', 'E', 'W']
        sources = [f'source_{d}' for d in directions]
        sinks = [f'sink_{d}' for d in directions]
        
        temp_graph.add_nodes_from(sources + ['intersection'] + sinks)
        temp_graph.add_node('super_source')
        temp_graph.add_node('super_sink')
        
        vehicle_counts = self._get_current_vehicle_counts()
        
        for direction in directions:
            source = f'source_{direction}'
            sink = f'sink_{direction}'
            
            # Capacidades basadas en light_times temporales
            input_cap = min(vehicle_counts[direction], 
                           light_times[direction] * 2.0)  # 2 veh/seg
            output_cap = light_times[direction] * 2.0
            
            temp_graph.add_edge(source, 'intersection', capacity=input_cap)
            temp_graph.add_edge('intersection', sink, capacity=output_cap)
            
            # Conectar a súper nodos
            temp_graph.add_edge('super_source', source, 
                               capacity=vehicle_counts[direction])
            temp_graph.add_edge(sink, 'super_sink', capacity=float('inf'))
        
        return temp_graph
    
    def _calculate_max_flow(self, graph):
        """Calcula flujo máximo en el grafo"""
        try:
            flow_value, _ = nx.maximum_flow(graph, 'super_source', 'super_sink')
            return flow_value
        except:
            return 0
    
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
    
    # Métodos auxiliares para métricas
    def _count_total_vehicles_passed(self):
        """Cuenta vehículos que han pasado por la intersección"""
        total = 0
        for light in self.intersection.traffic_lights.values():
            total += light.passing_vehicles
        return total
    
    def _calculate_average_waiting_time(self):
        """Calcula tiempo promedio de espera estimado"""
        total_waiting = 0
        total_vehicles = 0
        
        for direction in ['N', 'S', 'E', 'W']:
            vehicles_count = len(self.intersection.vehicles[direction])
            if vehicles_count > 0:
                # Estimación simple del tiempo de espera
                light = self.intersection.traffic_lights[direction]
                if light.state in ('RED', 'YELLOW'):
                    avg_wait = light.green_time / 2  # Estimación
                else:
                    avg_wait = 0
                
                total_waiting += avg_wait * vehicles_count
                total_vehicles += vehicles_count
        
        return total_waiting / max(1, total_vehicles)
    
    def _calculate_current_flow_rate(self):
        """Calcula tasa de flujo actual"""
        if not self.metrics_history['vehicles_passed']:
            return 0
        
        # Tasa basada en vehículos que han pasado recientemente
        recent_count = len(self.metrics_history['vehicles_passed'])
        if recent_count >= 2:
            time_diff = (self.metrics_history['timestamp'][-1] - 
                        self.metrics_history['timestamp'][-2])
            vehicle_diff = (self.metrics_history['vehicles_passed'][-1] - 
                           self.metrics_history['vehicles_passed'][-2])
            
            return vehicle_diff / max(0.1, time_diff)  # vehículos por segundo
        
        return 0
    
    def _generate_optimization_report(self):
        """Genera reporte final de optimización"""
        if not self.metrics_history['vehicles_passed']:
            return "No hay datos suficientes para generar reporte"
        
        total_vehicles = self.metrics_history['vehicles_passed'][-1]
        avg_waiting_time = np.mean(self.metrics_history['waiting_times'])
        max_flow_rate = max(self.metrics_history['total_flow']) if self.metrics_history['total_flow'] else 0
        
        report = f"""
📈 VEHÍCULOS TOTALES PROCESADOS: {total_vehicles}
⏱️  TIEMPO PROMEDIO DE ESPERA: {avg_waiting_time:.2f} segundos
🚀 TASA MÁXIMA DE FLUJO: {max_flow_rate:.2f} veh/seg
⚙️  CONFIGURACIÓN ÓPTIMA: {self.current_optimal_times}
⏰ TIEMPO DE SIMULACIÓN: {self.simulation_time_limit} segundos

💡 EFICIENCIA: {(total_vehicles/self.simulation_time_limit)*60:.1f} vehículos/minuto
        """
        
        return report
    
    def _save_results_to_file(self):
        """Guarda resultados en archivo JSON"""
        results = {
            'optimization_results': {
                'optimal_light_times': self.current_optimal_times,
                'simulation_time_limit': self.simulation_time_limit,
                'final_metrics': {
                    'total_vehicles_passed': self.metrics_history['vehicles_passed'][-1] if self.metrics_history['vehicles_passed'] else 0,
                    'average_waiting_time': np.mean(self.metrics_history['waiting_times']) if self.metrics_history['waiting_times'] else 0,
                    'max_flow_rate': max(self.metrics_history['total_flow']) if self.metrics_history['total_flow'] else 0
                }
            },
            'metrics_history': self.metrics_history
        }
        
        filename = f"traffic_optimization_results_{int(time.time())}.json"
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"📄 Resultados guardados en: {filename}")
    
    def _plot_optimization_results(self):
        """Genera gráficos de los resultados"""
        if not self.metrics_history['timestamp']:
            return
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        timestamps = self.metrics_history['timestamp']
        
        # Gráfico 1: Vehículos acumulados
        ax1.plot(timestamps, self.metrics_history['vehicles_passed'], 'b-', linewidth=2)
        ax1.set_title('Vehículos Procesados vs Tiempo')
        ax1.set_xlabel('Tiempo (s)')
        ax1.set_ylabel('Vehículos Acumulados')
        ax1.grid(True)
        
        # Gráfico 2: Tiempo de espera
        if self.metrics_history['waiting_times']:
            ax2.plot(timestamps, self.metrics_history['waiting_times'], 'r-', linewidth=2)
            ax2.set_title('Tiempo Promedio de Espera')
            ax2.set_xlabel('Tiempo (s)')
            ax2.set_ylabel('Tiempo de Espera (s)')
            ax2.grid(True)
        
        # Gráfico 3: Tasa de flujo
        if self.metrics_history['total_flow']:
            ax3.plot(timestamps, self.metrics_history['total_flow'], 'g-', linewidth=2)
            ax3.set_title('Tasa de Flujo')
            ax3.set_xlabel('Tiempo (s)')
            ax3.set_ylabel('Vehículos/segundo')
            ax3.grid(True)
        
        # Gráfico 4: Configuración de semáforos
        if self.current_optimal_times:
            directions = list(self.current_optimal_times.keys())
            times = list(self.current_optimal_times.values())
            ax4.bar(directions, times, color=['red', 'blue', 'green', 'orange'])
            ax4.set_title('Tiempos Óptimos de Semáforo')
            ax4.set_xlabel('Dirección')
            ax4.set_ylabel('Tiempo Verde (s)')
            ax4.grid(True)
        
        plt.tight_layout()
        plt.savefig(f'optimization_results_{int(time.time())}.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    # Métodos auxiliares para algoritmo genético
    def _tournament_selection(self, fitness_scores, size):
        """Selección por torneo"""
        selected = []
        for _ in range(size):
            tournament = np.random.choice(len(fitness_scores), 3, replace=False)
            winner_idx = min(tournament)  # Mejor fitness (mayor valor)
            selected.append(fitness_scores[winner_idx][1])
        return selected
    
    def _smart_crossover(self, parent1, parent2):
        """Crossover que respeta restricciones"""
        child = {}
        
        # Hacer crossover normal primero
        for direction in ['N', 'S', 'E', 'W']:
            weight = np.random.random()
            child[direction] = int(parent1[direction] * weight + 
                                parent2[direction] * (1 - weight))
            child[direction] = np.clip(child[direction], 
                                    self.min_green_time, 
                                    self.max_green_time)
        
        # CORRECCIÓN: Ajustar para que sume cycle_time
        current_total = sum(child.values())
        if current_total != self.cycle_time:
            factor = self.cycle_time / current_total
            for direction in child:
                child[direction] = max(
                    self.min_green_time,
                    min(self.max_green_time, int(child[direction] * factor))
                )
            
            # Ajuste fino
            current_total = sum(child.values())
            diff = self.cycle_time - current_total
            
            if diff != 0:
                # Ajustar dirección aleatoria
                direction = np.random.choice(['N', 'S', 'E', 'W'])
                child[direction] = max(
                    self.min_green_time,
                    min(self.max_green_time, child[direction] + diff)
                )
        
        return child
    
    def _adaptive_mutation(self, individual):
        """Mutación adaptiva"""
        mutated = individual.copy()
        direction = np.random.choice(['N', 'S', 'E', 'W'])
        
        # Mutación basada en la desviación de la media
        current_time = mutated[direction]
        mean_time = np.mean(list(mutated.values()))
        
        if current_time > mean_time:
            change = np.random.randint(-8, 3)  # Más probable decrecer
        else:
            change = np.random.randint(-3, 8)  # Más probable incrementar
        
        mutated[direction] = np.clip(current_time + change, 
                                   self.min_green_time, 
                                   self.max_green_time)
        return mutated
    
    def _calculate_balance_penalty(self, light_times):
        """Penaliza configuraciones muy desbalanceadas"""
        times = list(light_times.values())
        std_dev = np.std(times)
        return std_dev * 0.1  # Penalidad proporcional a la desviación
    
    def _calculate_time_efficiency(self, light_times):
        """Calcula eficiencia de uso del tiempo disponible"""
        total_time = sum(light_times.values())
        efficiency = min(1.0, total_time / self.cycle_time)
        return efficiency * 10  # Escalar para el fitness
    
    def _estimate_waiting_time_reduction(self, light_times):
        """Estima reducción en tiempo de espera"""
        vehicle_counts = self._get_current_vehicle_counts()
        total_reduction = 0
        
        for direction in ['N', 'S', 'E', 'W']:
            if vehicle_counts[direction] > 0:
                # Tiempo de procesamiento estimado
                processing_time = vehicle_counts[direction] / 2.0  # 2 veh/seg
                green_time = light_times[direction]
                
                if green_time >= processing_time:
                    total_reduction += processing_time
                else:
                    total_reduction += green_time
        
        return total_reduction

# Función principal para integrar con main.py
def create_traffic_optimizer(intersection):
    """
    Crea y retorna un optimizador para la intersección
    """
    return TrafficFlowOptimizer(intersection)


# Método para debugging
def debug_optimization_state(self):
    """Método para verificar el estado de la optimización"""
    vehicle_counts = self._get_current_vehicle_counts()
    current_times = self._get_current_light_times()
    
    print("\n🔍 DEBUG - Estado de optimización:")
    print(f"Vehículos por dirección: {vehicle_counts}")
    print(f"Tiempos actuales: {current_times}")
    print(f"Suma tiempos: {sum(current_times.values())}")
    print(f"Cycle time configurado: {self.cycle_time}")
    
    # Calcular distribución óptima teórica
    total_vehicles = sum(vehicle_counts.values())
    if total_vehicles > 0:
        print("\n📊 Distribución teórica óptima:")
        remaining_time = self.cycle_time - (4 * self.min_green_time)
        
        for direction in ['N', 'S', 'E', 'W']:
            ratio = vehicle_counts[direction] / total_vehicles
            optimal_time = self.min_green_time + (remaining_time * ratio)
            print(f"  {direction}: {optimal_time:.1f}s (vehículos: {vehicle_counts[direction]})")