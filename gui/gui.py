import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import networkx as nx
import contextily as ctx
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
import contextily as ctx
from core.algorithms import (
    get_shortest_path_dijkstra,
    get_shortest_path_astar,
    greedy_search,
    design_mst_network,
    optimize_traffic_signal,
    adjust_signal_for_emergency,
    schedule_transit,
    optimize_road_maintenance,
    get_time_dependent_path
)

class CairoMapGUI:
    def __init__(self, master, cairo_map):
        self.master = master
        self.cairo_map = cairo_map
        master.title("Smart Transportation System - Cairo")
        master.geometry("1300x800")
        plt.ioff()

        # تعريف متغيرات التحكم
        self.show_metro = tk.BooleanVar(value=True)
        self.show_bus = tk.BooleanVar(value=True)
        
        # إنشاء واجهة المستخدم
        self.create_control_frame()
        self.create_map_frame()
        self.setup_algorithm_tabs()
        self.populate_locations()
        
    def create_control_frame(self):
        """Create the left control section"""
        self.control_frame = tk.Frame(self.master, padx=10, pady=10, width=400)
        self.control_frame.pack(side=tk.LEFT, fill=tk.BOTH)
        
        # System title
        title = tk.Label(self.control_frame, text="Smart Transportation System", font=("Arial", 16, "bold"))
        title.pack(pady=10)

    def create_map_frame(self):
        """Create the map display section"""
        self.map_frame = tk.Frame(self.master, padx=10, pady=10)
        self.map_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)
        
        # حجم الشكل الأصلي (أصغر قليلاً)
        self.fig = plt.Figure(figsize=(8, 6), dpi=100)
        self.ax = self.fig.add_subplot(111)
        
        # إضافة Canvas مع شريط أدوات التنقل (للتكبير/التصغير)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.map_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # إضافة شريط أدوات التكبير/التصغير
        toolbar = NavigationToolbar2Tk(self.canvas, self.map_frame)
        toolbar.update()
        self.canvas._tkcanvas.pack(fill=tk.BOTH, expand=True)
        
        self.draw_base_map()

    def setup_algorithm_tabs(self):
        """Set up tabs for different algorithms"""
        # إضافة إطار للخيارات العامة فوق التبويبات
        options_frame = ttk.Frame(self.control_frame)
        options_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # إضافة خيارات التحكم
        ttk.Checkbutton(options_frame, 
                    text="Show Metro Lines", 
                    variable=self.show_metro,
                    command=self.draw_base_map).pack(side=tk.LEFT, padx=5)
        
        ttk.Checkbutton(options_frame, 
                    text="Show Bus Routes", 
                    variable=self.show_bus,
                    command=self.draw_base_map).pack(side=tk.LEFT, padx=5)
        
        # إنشاء تبويبات الخوارزميات
        tab_control = ttk.Notebook(self.control_frame)
        
        # تبويب البحث عن المسار
        path_tab = ttk.Frame(tab_control)
        self.setup_path_tab(path_tab)
        
        # تبويب حالة الطوارئ
        emergency_tab = ttk.Frame(tab_control)
        self.setup_emergency_tab(emergency_tab)
        
        # تبويب صيانة الطرق
        maintenance_tab = ttk.Frame(tab_control)
        self.setup_maintenance_tab(maintenance_tab)
        
        # تبويب النقل العام
        transit_tab = ttk.Frame(tab_control)
        self.setup_transit_tab(transit_tab)
        
        tab_control.add(path_tab, text="Find Path")
        tab_control.add(emergency_tab, text="Emergency Mode")
        tab_control.add(maintenance_tab, text="Road Maintenance")
        tab_control.add(transit_tab, text="Public Transit")
        tab_control.pack(expand=1, fill="both")

    def setup_path_tab(self, parent):
        """Setup interface for pathfinding"""
        frame = ttk.LabelFrame(parent, text="Path Options")
        frame.pack(fill=tk.BOTH, padx=5, pady=5)
        
        # Start point
        ttk.Label(frame, text="Start Point:").grid(row=0, column=0, sticky="w")
        self.start_var = tk.StringVar()
        self.start_combo = ttk.Combobox(frame, textvariable=self.start_var, width=25)
        self.start_combo.grid(row=0, column=1, pady=5)
        
        # End point
        ttk.Label(frame, text="End Point:").grid(row=1, column=0, sticky="w")
        self.end_var = tk.StringVar()
        self.end_combo = ttk.Combobox(frame, textvariable=self.end_var, width=25)
        self.end_combo.grid(row=1, column=1, pady=5)
        
        # Algorithm type
        ttk.Label(frame, text="Algorithm:").grid(row=2, column=0, sticky="w")
        self.algo_var = tk.StringVar()
        algo_combo = ttk.Combobox(frame, textvariable=self.algo_var, width=25,
                                 values=["Dijkstra", "A*", "Greedy", "Time-dependent Dijkstra", "MST"])
        algo_combo.current(0)
        algo_combo.grid(row=2, column=1, pady=5)
        
        # Time of day (for Time-dependent Dijkstra)
        ttk.Label(frame, text="Time of Day (0-23):").grid(row=3, column=0, sticky="w")
        self.time_var = tk.IntVar(value=8)
        ttk.Scale(frame, from_=0, to=23, variable=self.time_var, orient=tk.HORIZONTAL).grid(row=3, column=1, pady=5)
        
        # Search button
        ttk.Button(frame, text="Find Path", command=self.find_path).grid(row=4, column=0, columnspan=2, pady=10)
        
        # Path information display
        self.path_info = tk.Text(frame, height=10, width=40, state=tk.DISABLED)
        self.path_info.grid(row=5, column=0, columnspan=2)

    def setup_emergency_tab(self, parent):
        """Setup interface for emergency mode"""
        frame = ttk.LabelFrame(parent, text="Emergency Control")
        frame.pack(fill=tk.BOTH, padx=5, pady=5)
        
        # Emergency vehicle direction
        ttk.Label(frame, text="Emergency Vehicle Direction:").pack()
        self.emergency_dir = tk.StringVar()
        ttk.Combobox(frame, textvariable=self.emergency_dir, 
                     values=["north", "south", "east", "west"]).pack(pady=5)
        
        # Traffic data (can be fetched from the system)
        self.traffic_data = {
            "north": 50,
            "south": 30,
            "east": 70,
            "west": 20
        }
        
        # Activation button
        ttk.Button(frame, text="Activate Emergency Mode", 
                   command=self.activate_emergency).pack(pady=10)
        
        # Result display
        self.emergency_result = tk.Text(frame, height=8, width=40, state=tk.DISABLED)
        self.emergency_result.pack()

    def setup_maintenance_tab(self, parent):
        """Setup interface for road maintenance"""
        frame = ttk.LabelFrame(parent, text="Maintenance Allocation")
        frame.pack(fill=tk.BOTH, padx=5, pady=5)
        
        # Budget input
        ttk.Label(frame, text="Available Budget:").pack()
        self.budget_var = tk.IntVar(value=1000)
        ttk.Entry(frame, textvariable=self.budget_var).pack(pady=5)
        
        # Optimization button
        ttk.Button(frame, text="Optimize Maintenance", 
                   command=self.optimize_maintenance).pack(pady=10)
        
        # Result display
        self.maintenance_result = tk.Text(frame, height=8, width=40, state=tk.DISABLED)
        self.maintenance_result.pack()

    def setup_transit_tab(self, parent):
        """Setup interface for public transit scheduling"""
        frame = ttk.LabelFrame(parent, text="Transit Scheduling")
        frame.pack(fill=tk.BOTH, padx=5, pady=5)
        
        # Number of buses
        ttk.Label(frame, text="Number of Available Buses:").pack()
        self.buses_var = tk.IntVar(value=30)
        ttk.Entry(frame, textvariable=self.buses_var).pack(pady=5)
        
        # Schedule button
        ttk.Button(frame, text="Create Schedule", 
                   command=self.schedule_transit).pack(pady=10)
        
        # Result display
        self.transit_result = tk.Text(frame, height=8, width=40, state=tk.DISABLED)
        self.transit_result.pack()

    def populate_locations(self):
        """Populate location lists for selection"""
        locations = []
        for node in self.cairo_map.G.nodes():
            data = self.cairo_map.G.nodes[node]
            name = data.get('name', node)
            locations.append((node, f"{name} ({node})"))
        
        locations.sort(key=lambda x: x[1])
        display_names = [dn for _, dn in locations]
        
        self.start_combo['values'] = display_names
        self.end_combo['values'] = display_names
        if display_names:
            self.start_combo.current(0)
            self.end_combo.current(min(1, len(display_names)-1))


# في بداية الملف، تأكد من وجود الاستيراد التالي

    # ثم عدل دالة draw_base_map كما يلي:
    def draw_base_map(self):
        """Draw the base map with real Cairo map background"""
        self.ax.clear()
        pos = {node: data.get('pos', (0, 0)) for node, data in self.cairo_map.G.nodes(data=True)}
        
        # تحويل الإحداثيات إلى نظام إسقاط مناسب (مثال: WGS84)
        # لاحظ أن إحداثياتك الحالية تبدو كإحداثيات خطوط الطول والعرض
        # إذا كانت بالفعل كذلك، يمكن استخدامها مباشرة
        node_positions = {node: (data['pos'][0], data['pos'][1]) 
                        for node, data in self.cairo_map.G.nodes(data=True) if 'pos' in data}
        
        # فصل العقد إلى أحياء ومرافق
        neighborhoods = []
        facilities = []
        
        for node in self.cairo_map.G.nodes():
            node_data = self.cairo_map.G.nodes[node]
            if node_data.get('node_type') == 'neighborhood':
                neighborhoods.append(node)
            elif node_data.get('node_type') == 'facility':
                facilities.append(node)
        
        # رسم الخريطة الأساسية
        if node_positions:
            # الحصول على حدود الخريطة بناءً على مواقع العقد
            all_x = [pos[0] for pos in node_positions.values()]
            all_y = [pos[1] for pos in node_positions.values()]
            min_x, max_x = min(all_x), max(all_x)
            min_y, max_y = min(all_y), max(all_y)
            
            # توسيع الحدود قليلاً
            padding = 0.02
            min_x -= padding
            max_x += padding
            min_y -= padding
            max_y += padding
            
            # تعيين حدود المحور
            self.ax.set_xlim(min_x, max_x)
            self.ax.set_ylim(min_y, max_y)
            
            # إضافة خريطة القاعدة (قد تحتاج إلى ضبط مستوى التكبير)
            try:
                ctx.add_basemap(
                    self.ax,
                    crs='EPSG:4326',  # نظام إحداثيات WGS84
                    source=ctx.providers.OpenStreetMap.Mapnik,
                    zoom=12  # يمكن ضبط مستوى التكبير حسب الحاجة
                )
            except Exception as e:
                print(f"Error loading basemap: {e}")
                # إذا فشل تحميل الخريطة، ارسم بدونها
                pass
        
        # رسم الطرق
        nx.draw_networkx_edges(
            self.cairo_map.G, pos, 
            edge_color="#4d4d4d", 
            width=1, 
            ax=self.ax
        )
        
        # رسم الأحياء باللون الأخضر
        nx.draw_networkx_nodes(
            self.cairo_map.G, pos,
            nodelist=neighborhoods,
            node_size=100,  # تصغير حجم العقد لتناسب الخريطة
            node_color="#66c2a5",
            ax=self.ax,
            alpha=0.8
        )
        
        # رسم المرافق باللون البرتقالي
        nx.draw_networkx_nodes(
            self.cairo_map.G, pos,
            nodelist=facilities,
            node_size=100,
            node_color="#ff7f0e",
            ax=self.ax,
            node_shape='s',
            alpha=0.8
        )
        
        # تسميات العقد (يمكن تقليل حجم الخط)
        labels = {n: d.get('name', n) for n, d in self.cairo_map.G.nodes(data=True)}
        nx.draw_networkx_labels(
            self.cairo_map.G, pos,
            labels=labels,
            font_size=8,
            ax=self.ax,
            font_color='black',
            bbox=dict(facecolor='white', alpha=0.7, edgecolor='none')
        )
        
        # إضافة وسيلة الإيضاح
        legend_elements = [
            Patch(facecolor='#66c2a5', edgecolor='black', label='Neighborhoods'),
            Patch(facecolor='#ff7f0e', edgecolor='black', label='Facilities'),
            Line2D([0], [0], color='#4d4d4d', lw=2, label='Existing Roads'),
            Line2D([0], [0], color='#4d4d4d', lw=2, linestyle='dotted', label='Proposed Roads')
        ]
        
        # إضافة خطوط المترو والباصات إذا كانت مفعلة
        if hasattr(self, 'show_metro') and self.show_metro.get():
            self.draw_metro_lines()
            legend_elements.append(Line2D([0], [0], color='red', lw=2, label='Metro Lines'))
        
        if hasattr(self, 'show_bus') and self.show_bus.get():
            self.draw_bus_routes()
            legend_elements.append(Line2D([0], [0], color='blue', lw=2, linestyle='--', label='Bus Routes'))
        
        self.ax.legend(handles=legend_elements, loc='upper right')
        self.ax.set_title("Cairo Transportation Network Map")
        self.ax.axis('off')
        self.canvas.draw()

    def draw_metro_lines(self):
        """Draw metro lines on the map"""
        pos = {node: data.get('pos', (0, 0)) for node, data in self.cairo_map.G.nodes(data=True)}
        
        for line in self.cairo_map.metro_lines:
            stations = line["stations"]
            line_color = self.get_line_color(line["line_id"])
            
            # Draw line segments between stations
            for i in range(len(stations)-1):
                start = str(stations[i])
                end = str(stations[i+1])
                
                if start in pos and end in pos:
                    x_values = [pos[start][0], pos[end][0]]
                    y_values = [pos[start][1], pos[end][1]]
                    self.ax.plot(x_values, y_values, color=line_color, linewidth=3, alpha=0.7)
                    
                    # Add line label at midpoint
                    midpoint_x = (pos[start][0] + pos[end][0]) / 2
                    midpoint_y = (pos[start][1] + pos[end][1]) / 2
                    self.ax.text(midpoint_x, midpoint_y, line["line_id"], 
                                color=line_color, fontsize=8, weight='bold',
                                bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))

    def draw_bus_routes(self):
        """Draw bus routes on the map"""
        pos = {node: data.get('pos', (0, 0)) for node, data in self.cairo_map.G.nodes(data=True)}
        
        for route in self.cairo_map.bus_routes:
            stops = route["stops"]
            
            # Draw line segments between stops
            for i in range(len(stops)-1):
                start = str(stops[i])
                end = str(stops[i+1])
                
                if start in pos and end in pos:
                    x_values = [pos[start][0], pos[end][0]]
                    y_values = [pos[start][1], pos[end][1]]
                    self.ax.plot(x_values, y_values, color='blue', linewidth=1.5, linestyle='--', alpha=0.5)
                    
                    # Add route label at first stop
                    if i == 0:
                        self.ax.text(pos[start][0], pos[start][1], route["route_id"], 
                                    color='blue', fontsize=7,
                                    bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))

    def get_line_color(self, line_id):
        """Return color based on metro line ID"""
        colors = {
            "M1": "red",
            "M2": "green",
            "M3": "blue"
        }
        return colors.get(line_id, "purple")

    def toggle_metro(self):
        """Toggle visibility of metro lines"""
        self.draw_base_map()

    def toggle_bus(self):
        """Toggle visibility of bus routes"""
        self.draw_base_map()

    def find_path(self):
        """Find path using selected algorithm"""
        start = self.extract_node_id(self.start_var.get())
        end = self.extract_node_id(self.end_var.get())
        algo = self.algo_var.get()
        
        if not start or not end:
            messagebox.showerror("Error", "Please select start and end points")
            return
            
        path = None
        info = ""
        
        try:
            if algo == "Dijkstra":
                path, length = get_shortest_path_dijkstra(self.cairo_map.G, start, end)
                info = f"Shortest Path (Dijkstra)\nLength: {length:.2f} km\n\n"
            elif algo == "A*":
                path, length = get_shortest_path_astar(self.cairo_map.G, start, end)
                info = f"Shortest Path (A*)\nLength: {length:.2f} km\n\n"
            elif algo == "Greedy":
                path = greedy_search(self.cairo_map.G, start, end)
                info = "Path (Greedy)\n\n"
            elif algo == "Time-dependent Dijkstra":
                path, length = get_time_dependent_path(self.cairo_map.G, start, end, self.time_var.get())
                info = f"Time-dependent Path\nTime: {length:.2f} minutes\n\n"
            elif algo == "MST":
                mst = design_mst_network(self.cairo_map.G)
                self.draw_mst(mst)
                info = "Minimum Spanning Tree Network\n"
                self.update_path_info(info)
                return
                
            if path:
                info += "Path:\n" + " → ".join([self.cairo_map.G.nodes[n].get('name', n) for n in path])
                self.draw_path(path)
            else:
                info = "No available path!"
                
            self.update_path_info(info)
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def activate_emergency(self):
        """Activate emergency mode"""
        direction = self.emergency_dir.get()
        if not direction:
            messagebox.showerror("Error", "Please select an emergency vehicle direction")
            return
            
        try:
            result = adjust_signal_for_emergency(self.traffic_data, direction)
            text = "Traffic Signal Distribution:\n"
            for dir, time in result.items():
                text += f"{dir}: {time}%\n"
                
            self.emergency_result.config(state=tk.NORMAL)
            self.emergency_result.delete(1.0, tk.END)
            self.emergency_result.insert(tk.END, text)
            self.emergency_result.config(state=tk.DISABLED)
            
            messagebox.showinfo("Success", "Emergency mode activated successfully")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def optimize_maintenance(self):
        """Optimize road maintenance"""
        roads = [
            {"road_id": "1-3", "repair_cost": 500, "urgency": 7},
            {"road_id": "2-5", "repair_cost": 300, "urgency": 9},
            {"road_id": "3-6", "repair_cost": 200, "urgency": 5}
        ]
        
        selected, total = optimize_road_maintenance(roads, self.budget_var.get())
        
        text = f"Selected roads (Total importance: {total}):\n"
        for road in selected:
            text += f"{road['road_id']} (Cost: {road['repair_cost']}, Urgency: {road['urgency']})\n"
            
        self.maintenance_result.config(state=tk.NORMAL)
        self.maintenance_result.delete(1.0, tk.END)
        self.maintenance_result.insert(tk.END, text)
        self.maintenance_result.config(state=tk.DISABLED)

    def schedule_transit(self):
        """Schedule public transit"""
        lines = [
            {"line_id": "M1", "start_time": 6, "end_time": 22, "passenger_demand": 1500000},
            {"line_id": "M2", "start_time": 7, "end_time": 23, "passenger_demand": 1200000}
        ]
        
        selected, total = schedule_transit(lines, self.buses_var.get())
        
        text = f"Selected lines (Total passengers: {total}):\n"
        for line in selected:
            text += f"{line['line_id']} (Passengers: {line['passenger_demand']})\n"
            
        self.transit_result.config(state=tk.NORMAL)
        self.transit_result.delete(1.0, tk.END)
        self.transit_result.insert(tk.END, text)
        self.transit_result.config(state=tk.DISABLED)

    def draw_path(self, path):
        """Draw the path on the map"""
        pos = {node: data.get('pos', (0, 0)) for node, data in self.cairo_map.G.nodes(data=True)}
        path_edges = list(zip(path[:-1], path[1:]))
        
        self.draw_base_map()
        nx.draw_networkx_edges(
            self.cairo_map.G, pos,
            edgelist=path_edges,
            edge_color="red",
            width=3,
            ax=self.ax
        )
        self.canvas.draw()

    def draw_mst(self, mst):
        """Draw the Minimum Spanning Tree"""
        pos = {node: data.get('pos', (0, 0)) for node, data in self.cairo_map.G.nodes(data=True)}
        
        self.draw_base_map()
        nx.draw_networkx_edges(
            mst, pos,
            edge_color="blue",
            width=2,
            ax=self.ax
        )
        self.canvas.draw()

    def update_path_info(self, text):
        """Update the path information display"""
        self.path_info.config(state=tk.NORMAL)
        self.path_info.delete(1.0, tk.END)
        self.path_info.insert(tk.END, text)
        self.path_info.config(state=tk.DISABLED)

    def extract_node_id(self, display_text):
        """Extract node ID from display text"""
        if not display_text:
            return None
        if "(" in display_text and ")" in display_text:
            return display_text.split("(")[-1].split(")")[0].strip()
        return display_text.strip()