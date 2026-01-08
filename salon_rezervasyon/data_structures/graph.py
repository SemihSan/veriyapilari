"""
Graf ve Yol Bulma Algoritmaları
===============================
Salon/oda bağlantıları için graf yapısı ve en kısa yol algoritmaları.
BFS, Dijkstra ve A* algoritmalarını içerir.

Zaman Karmaşıklığı:
- BFS: O(V + E)
- Dijkstra: O((V + E) log V) - binary heap ile
- A*: O(E) - iyi heuristic ile, en kötü O(V²)

Uzay Karmaşıklığı: O(V + E)
"""

from typing import Any, Dict, List, Optional, Set, Tuple, Callable
from collections import defaultdict
import math

# Heap modülünden import
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from heap import MinHeap, PriorityQueue


class Graph:
    """
    Graf Veri Yapısı - Adjacency List implementasyonu
    
    Kullanım Alanları:
    - Salonlar arası mesafe/bağlantı modellemesi
    - Bina içi navigasyon
    - Salon öneri sistemi (benzer salonları bulma)
    """
    
    def __init__(self, directed: bool = False):
        """
        Args:
            directed: Yönlü graf mı?
        """
        self.directed = directed
        self.adjacency_list: Dict[Any, List[Tuple[Any, float]]] = defaultdict(list)
        self.vertices: Set[Any] = set()
        self.vertex_data: Dict[Any, Any] = {}  # Düğüm verileri (salon bilgileri)
    
    def add_vertex(self, vertex: Any, data: Any = None) -> None:
        """
        Grafa düğüm ekle
        
        Args:
            vertex: Düğüm kimliği
            data: Düğüm verisi (opsiyonel)
            
        Zaman Karmaşıklığı: O(1)
        """
        self.vertices.add(vertex)
        if vertex not in self.adjacency_list:
            self.adjacency_list[vertex] = []
        if data is not None:
            self.vertex_data[vertex] = data
    
    def add_edge(self, u: Any, v: Any, weight: float = 1.0) -> None:
        """
        Grafa kenar ekle
        
        Args:
            u: Kaynak düğüm
            v: Hedef düğüm
            weight: Kenar ağırlığı (mesafe, süre vb.)
            
        Zaman Karmaşıklığı: O(1)
        """
        self.add_vertex(u)
        self.add_vertex(v)
        
        self.adjacency_list[u].append((v, weight))
        
        if not self.directed:
            self.adjacency_list[v].append((u, weight))
    
    def remove_vertex(self, vertex: Any) -> bool:
        """
        Düğümü ve bağlı kenarları kaldır
        
        Zaman Karmaşıklığı: O(V + E)
        """
        if vertex not in self.vertices:
            return False
        
        # Düğümü kaldır
        self.vertices.remove(vertex)
        del self.adjacency_list[vertex]
        
        # Diğer düğümlerden bu düğüme giden kenarları kaldır
        for v in self.vertices:
            self.adjacency_list[v] = [(n, w) for n, w in self.adjacency_list[v] if n != vertex]
        
        if vertex in self.vertex_data:
            del self.vertex_data[vertex]
        
        return True
    
    def remove_edge(self, u: Any, v: Any) -> bool:
        """
        Kenarı kaldır
        
        Zaman Karmaşıklığı: O(E)
        """
        if u not in self.vertices or v not in self.vertices:
            return False
        
        original_len = len(self.adjacency_list[u])
        self.adjacency_list[u] = [(n, w) for n, w in self.adjacency_list[u] if n != v]
        
        if not self.directed:
            self.adjacency_list[v] = [(n, w) for n, w in self.adjacency_list[v] if n != u]
        
        return len(self.adjacency_list[u]) < original_len
    
    def get_neighbors(self, vertex: Any) -> List[Tuple[Any, float]]:
        """Komşu düğümleri döndür"""
        return self.adjacency_list.get(vertex, [])
    
    def has_vertex(self, vertex: Any) -> bool:
        """Düğüm var mı?"""
        return vertex in self.vertices
    
    def has_edge(self, u: Any, v: Any) -> bool:
        """Kenar var mı?"""
        return any(n == v for n, _ in self.adjacency_list.get(u, []))
    
    def get_edge_weight(self, u: Any, v: Any) -> Optional[float]:
        """Kenar ağırlığını döndür"""
        for neighbor, weight in self.adjacency_list.get(u, []):
            if neighbor == v:
                return weight
        return None
    
    def vertex_count(self) -> int:
        """Düğüm sayısı"""
        return len(self.vertices)
    
    def edge_count(self) -> int:
        """Kenar sayısı"""
        total = sum(len(neighbors) for neighbors in self.adjacency_list.values())
        return total if self.directed else total // 2
    
    # ==================== BFS (Breadth-First Search) ====================
    
    def bfs(self, start: Any) -> List[Any]:
        """
        Genişlik Öncelikli Arama - Tüm erişilebilir düğümleri ziyaret et
        
        Args:
            start: Başlangıç düğümü
            
        Returns:
            Ziyaret sırasına göre düğüm listesi
            
        Zaman Karmaşıklığı: O(V + E)
        Uzay Karmaşıklığı: O(V)
        """
        if start not in self.vertices:
            return []
        
        visited = set()
        queue = [start]
        result = []
        
        while queue:
            vertex = queue.pop(0)  # FIFO
            
            if vertex not in visited:
                visited.add(vertex)
                result.append(vertex)
                
                for neighbor, _ in self.adjacency_list[vertex]:
                    if neighbor not in visited:
                        queue.append(neighbor)
        
        return result
    
    def bfs_shortest_path(self, start: Any, end: Any) -> Tuple[List[Any], int]:
        """
        BFS ile en kısa yol (ağırlıksız graf için)
        
        Args:
            start: Başlangıç düğümü
            end: Hedef düğüm
            
        Returns:
            (yol, mesafe) tuple - yol bulunamazsa ([], -1)
            
        Zaman Karmaşıklığı: O(V + E)
        """
        if start not in self.vertices or end not in self.vertices:
            return [], -1
        
        if start == end:
            return [start], 0
        
        visited = {start}
        queue = [(start, [start])]
        
        while queue:
            vertex, path = queue.pop(0)
            
            for neighbor, _ in self.adjacency_list[vertex]:
                if neighbor not in visited:
                    new_path = path + [neighbor]
                    
                    if neighbor == end:
                        return new_path, len(new_path) - 1
                    
                    visited.add(neighbor)
                    queue.append((neighbor, new_path))
        
        return [], -1
    
    # ==================== DFS (Depth-First Search) ====================
    
    def dfs(self, start: Any) -> List[Any]:
        """
        Derinlik Öncelikli Arama
        
        Args:
            start: Başlangıç düğümü
            
        Returns:
            Ziyaret sırasına göre düğüm listesi
            
        Zaman Karmaşıklığı: O(V + E)
        """
        if start not in self.vertices:
            return []
        
        visited = set()
        result = []
        
        def _dfs(vertex: Any):
            visited.add(vertex)
            result.append(vertex)
            
            for neighbor, _ in self.adjacency_list[vertex]:
                if neighbor not in visited:
                    _dfs(neighbor)
        
        _dfs(start)
        return result
    
    def dfs_iterative(self, start: Any) -> List[Any]:
        """DFS iteratif versiyon (stack kullanarak)"""
        if start not in self.vertices:
            return []
        
        visited = set()
        stack = [start]
        result = []
        
        while stack:
            vertex = stack.pop()  # LIFO
            
            if vertex not in visited:
                visited.add(vertex)
                result.append(vertex)
                
                # Komşuları ters sırada ekle (tutarlı traversal için)
                for neighbor, _ in reversed(self.adjacency_list[vertex]):
                    if neighbor not in visited:
                        stack.append(neighbor)
        
        return result
    
    # ==================== Dijkstra Algoritması ====================
    
    def dijkstra(self, start: Any, end: Any = None) -> Tuple[Dict[Any, float], Dict[Any, Any]]:
        """
        Dijkstra'nın En Kısa Yol Algoritması
        
        Args:
            start: Başlangıç düğümü
            end: Hedef düğüm (opsiyonel - belirtilirse erken durur)
            
        Returns:
            (distances, predecessors) tuple
            - distances: Her düğüme olan en kısa mesafe
            - predecessors: En kısa yoldaki önceki düğüm
            
        Zaman Karmaşıklığı: O((V + E) log V) - binary heap ile
        Uzay Karmaşıklığı: O(V)
        """
        if start not in self.vertices:
            return {}, {}
        
        # Mesafeler (başlangıçta sonsuz)
        distances = {v: float('inf') for v in self.vertices}
        distances[start] = 0
        
        # Yol izleme için önceki düğümler
        predecessors = {v: None for v in self.vertices}
        
        # Min-heap: (mesafe, düğüm)
        pq = PriorityQueue(min_priority=True)
        pq.enqueue(start, 0)
        
        visited = set()
        
        while pq:
            current, current_dist = pq.dequeue()
            
            # Zaten işlendiyse atla
            if current in visited:
                continue
            
            visited.add(current)
            
            # Hedefe ulaştıysak dur
            if end and current == end:
                break
            
            # Komşuları kontrol et
            for neighbor, weight in self.adjacency_list[current]:
                if neighbor in visited:
                    continue
                
                new_dist = current_dist + weight
                
                if new_dist < distances[neighbor]:
                    distances[neighbor] = new_dist
                    predecessors[neighbor] = current
                    pq.enqueue(neighbor, new_dist)
        
        return distances, predecessors
    
    def dijkstra_path(self, start: Any, end: Any) -> Tuple[List[Any], float]:
        """
        Dijkstra ile en kısa yolu bul
        
        Args:
            start: Başlangıç düğümü
            end: Hedef düğüm
            
        Returns:
            (yol, toplam_mesafe) tuple
            
        Zaman Karmaşıklığı: O((V + E) log V)
        """
        distances, predecessors = self.dijkstra(start, end)
        
        if distances.get(end, float('inf')) == float('inf'):
            return [], float('inf')
        
        # Yolu geri izle
        path = []
        current = end
        while current is not None:
            path.append(current)
            current = predecessors[current]
        
        path.reverse()
        return path, distances[end]
    
    # ==================== A* Algoritması ====================
    
    def a_star(self, start: Any, end: Any, heuristic: Callable[[Any, Any], float]) -> Tuple[List[Any], float]:
        """
        A* Yol Bulma Algoritması
        
        Args:
            start: Başlangıç düğümü
            end: Hedef düğüm
            heuristic: h(n) fonksiyonu - tahmini kalan maliyet
            
        Returns:
            (yol, toplam_maliyet) tuple
            
        Zaman Karmaşıklığı: O(E) iyi heuristic ile, en kötü O(V²)
        """
        if start not in self.vertices or end not in self.vertices:
            return [], float('inf')
        
        # g(n): başlangıçtan n'e gerçek maliyet
        g_score = {v: float('inf') for v in self.vertices}
        g_score[start] = 0
        
        # f(n) = g(n) + h(n): toplam tahmini maliyet
        f_score = {v: float('inf') for v in self.vertices}
        f_score[start] = heuristic(start, end)
        
        # Yol izleme
        predecessors = {}
        
        # Open set: (f_score, düğüm)
        open_set = PriorityQueue(min_priority=True)
        open_set.enqueue(start, f_score[start])
        
        in_open_set = {start}
        
        while open_set:
            current, _ = open_set.dequeue()
            in_open_set.discard(current)
            
            if current == end:
                # Yolu oluştur
                path = []
                while current in predecessors:
                    path.append(current)
                    current = predecessors[current]
                path.append(start)
                path.reverse()
                return path, g_score[end]
            
            for neighbor, weight in self.adjacency_list[current]:
                tentative_g = g_score[current] + weight
                
                if tentative_g < g_score[neighbor]:
                    predecessors[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + heuristic(neighbor, end)
                    
                    if neighbor not in in_open_set:
                        open_set.enqueue(neighbor, f_score[neighbor])
                        in_open_set.add(neighbor)
        
        return [], float('inf')
    
    # ==================== Graf Analiz ====================
    
    def is_connected(self) -> bool:
        """Graf bağlı mı? (tüm düğümler erişilebilir mi?)"""
        if not self.vertices:
            return True
        
        start = next(iter(self.vertices))
        visited = set(self.bfs(start))
        
        return len(visited) == len(self.vertices)
    
    def find_connected_components(self) -> List[Set[Any]]:
        """Bağlı bileşenleri bul"""
        visited = set()
        components = []
        
        for vertex in self.vertices:
            if vertex not in visited:
                component = set(self.bfs(vertex))
                visited.update(component)
                components.append(component)
        
        return components
    
    def has_cycle(self) -> bool:
        """Graf döngü içeriyor mu?"""
        visited = set()
        rec_stack = set()
        
        def _has_cycle(v: Any, parent: Any = None) -> bool:
            visited.add(v)
            rec_stack.add(v)
            
            for neighbor, _ in self.adjacency_list[v]:
                if neighbor not in visited:
                    if _has_cycle(neighbor, v):
                        return True
                elif self.directed and neighbor in rec_stack:
                    return True
                elif not self.directed and neighbor != parent:
                    return True
            
            rec_stack.remove(v)
            return False
        
        for vertex in self.vertices:
            if vertex not in visited:
                if _has_cycle(vertex):
                    return True
        
        return False
    
    def topological_sort(self) -> List[Any]:
        """
        Topolojik sıralama (yalnızca DAG için)
        
        Returns:
            Topolojik sırada düğüm listesi veya boş liste (döngü varsa)
        """
        if not self.directed:
            raise ValueError("Topolojik sıralama sadece yönlü graflar için geçerli")
        
        in_degree = {v: 0 for v in self.vertices}
        
        for v in self.vertices:
            for neighbor, _ in self.adjacency_list[v]:
                in_degree[neighbor] += 1
        
        queue = [v for v in self.vertices if in_degree[v] == 0]
        result = []
        
        while queue:
            vertex = queue.pop(0)
            result.append(vertex)
            
            for neighbor, _ in self.adjacency_list[vertex]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        if len(result) != len(self.vertices):
            return []  # Döngü var
        
        return result
    
    def __repr__(self):
        return f"Graph(vertices={len(self.vertices)}, edges={self.edge_count()}, directed={self.directed})"
    
    def visualize(self) -> str:
        """Grafı metin olarak görselleştir"""
        lines = [f"Graf ({'Yönlü' if self.directed else 'Yönsüz'})"]
        lines.append(f"Düğümler: {len(self.vertices)}, Kenarlar: {self.edge_count()}")
        lines.append("-" * 40)
        
        for vertex in sorted(self.vertices, key=str):
            neighbors = self.adjacency_list[vertex]
            if neighbors:
                neighbor_str = ", ".join(f"{n}({w:.1f})" for n, w in neighbors)
                lines.append(f"{vertex} -> {neighbor_str}")
            else:
                lines.append(f"{vertex} -> (bağlantı yok)")
        
        return "\n".join(lines)


# 2D koordinatlar için A* heuristic fonksiyonları
def euclidean_distance(pos1: Tuple[float, float], pos2: Tuple[float, float]) -> float:
    """Öklid mesafesi (kuş uçuşu)"""
    return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)


def manhattan_distance(pos1: Tuple[float, float], pos2: Tuple[float, float]) -> float:
    """Manhattan mesafesi (ızgara hareketi)"""
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])


# Kullanım örneği ve test
if __name__ == "__main__":
    print("=" * 60)
    print("Graf ve Yol Bulma Algoritmaları Test")
    print("=" * 60)
    
    # Bina içi salon haritası oluştur
    building = Graph(directed=False)
    
    # Salonları ekle (düğümler)
    rooms = {
        "Lobi": (0, 0),
        "Salon A": (10, 0),
        "Salon B": (20, 0),
        "Salon C": (10, 10),
        "Toplantı 1": (0, 10),
        "Toplantı 2": (20, 10),
        "Kafeterya": (10, 20),
        "Çıkış": (0, 20)
    }
    
    for room, pos in rooms.items():
        building.add_vertex(room, {"position": pos})
    
    # Koridorları ekle (kenarlar - mesafe olarak)
    corridors = [
        ("Lobi", "Salon A", 10),
        ("Salon A", "Salon B", 10),
        ("Lobi", "Toplantı 1", 10),
        ("Salon A", "Salon C", 10),
        ("Salon B", "Toplantı 2", 10),
        ("Toplantı 1", "Salon C", 10),
        ("Salon C", "Toplantı 2", 10),
        ("Toplantı 1", "Kafeterya", 10),
        ("Salon C", "Kafeterya", 10),
        ("Toplantı 2", "Kafeterya", 14),  # Çapraz koridor
        ("Kafeterya", "Çıkış", 10),
        ("Toplantı 1", "Çıkış", 10),
    ]
    
    for u, v, w in corridors:
        building.add_edge(u, v, w)
    
    print("\n" + building.visualize())
    
    # BFS testi
    print("\n" + "=" * 40)
    print("BFS - Lobi'den başlayarak gezinti:")
    bfs_result = building.bfs("Lobi")
    print(f"Ziyaret sırası: {' -> '.join(bfs_result)}")
    
    # BFS en kısa yol (kenar sayısı olarak)
    path, dist = building.bfs_shortest_path("Lobi", "Çıkış")
    print(f"\nLobi -> Çıkış (min kenar): {' -> '.join(path)} ({dist} kenar)")
    
    # DFS testi
    print("\n" + "=" * 40)
    print("DFS - Lobi'den başlayarak gezinti:")
    dfs_result = building.dfs("Lobi")
    print(f"Ziyaret sırası: {' -> '.join(dfs_result)}")
    
    # Dijkstra testi
    print("\n" + "=" * 40)
    print("Dijkstra - En kısa yol (mesafe):")
    
    path, distance = building.dijkstra_path("Lobi", "Çıkış")
    print(f"Lobi -> Çıkış: {' -> '.join(path)}")
    print(f"Toplam mesafe: {distance} birim")
    
    path2, distance2 = building.dijkstra_path("Salon B", "Kafeterya")
    print(f"\nSalon B -> Kafeterya: {' -> '.join(path2)}")
    print(f"Toplam mesafe: {distance2} birim")
    
    # A* testi
    print("\n" + "=" * 40)
    print("A* - En kısa yol (heuristic ile):")
    
    # Heuristic fonksiyonu oluştur
    def room_heuristic(room1, room2):
        pos1 = rooms.get(room1, (0, 0))
        pos2 = rooms.get(room2, (0, 0))
        return euclidean_distance(pos1, pos2)
    
    path_astar, cost_astar = building.a_star("Lobi", "Çıkış", room_heuristic)
    print(f"Lobi -> Çıkış (A*): {' -> '.join(path_astar)}")
    print(f"Toplam maliyet: {cost_astar} birim")
    
    # Graf analiz
    print("\n" + "=" * 40)
    print("Graf Analizi:")
    print(f"Bağlı mı?: {building.is_connected()}")
    print(f"Döngü var mı?: {building.has_cycle()}")
    print(f"Bağlı bileşen sayısı: {len(building.find_connected_components())}")
    
    # Tüm noktalardan mesafeler
    print("\n" + "=" * 40)
    print("Lobi'den tüm salonlara mesafeler:")
    distances, _ = building.dijkstra("Lobi")
    for room in sorted(distances.keys(), key=lambda x: distances[x]):
        print(f"  {room}: {distances[room]} birim")
