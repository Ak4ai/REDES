import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import ipaddress
import csv
import json
from datetime import datetime

class NetworkCalculatorGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Calculadora de Redes - Interface Planilha")
        self.root.geometry("1400x800")
        
        # Dados das redes
        self.networks_data = []
        self.show_inter_router_routes = tk.BooleanVar(value=False)
        self.show_inbound_routes = tk.BooleanVar(value=False)
        self.router_colors = ['#E8F0FE', '#E6F4EA', '#FEF7E0', '#FCE8E6', '#F3E8FD', '#E0F7FA'] # Cores de fundo suaves
        
        self.setup_ui()
        self.setup_calculator()
        
    def setup_calculator(self):
        """Inicializa a classe calculadora"""
        from exe import NetworkCalculator
        self.calculator = NetworkCalculator()
    
    def setup_ui(self):
        """Configura a interface do usuário"""
        
        # Título
        title_label = ttk.Label(self.root, text="Calculadora de Redes", 
                                font=("Arial", 16, "bold"))
        title_label.pack(pady=10)

        # Notebook para abas
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Aba da Calculadora
        calculator_tab = ttk.Frame(self.notebook)
        self.notebook.add(calculator_tab, text="Calculadora de Redes")

        # Aba da Tabela de Roteamento
        routing_tab = ttk.Frame(self.notebook)
        self.notebook.add(routing_tab, text="Tabela de Roteamento")

        # Configurar conteúdo da aba da calculadora
        self.setup_calculator_tab(calculator_tab)

        # Configurar conteúdo da aba de roteamento
        self.setup_routing_tab(routing_tab)

    def setup_calculator_tab(self, parent):
        """Configura o conteúdo da aba da calculadora"""
        # Frame para entrada de dados
        self.setup_input_frame(parent)
        
        # Frame para a tabela (estilo planilha)
        self.setup_table_frame(parent)
        
        # Frame para botões de ação
        self.setup_action_frame(parent)

    def setup_routing_tab(self, parent):
        """Configura a aba da tabela de roteamento"""
        # Frame principal da aba
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Frame para os links WAN
        wan_links_frame = ttk.LabelFrame(main_frame, text="Links WAN com Provedor (ISP)", padding=10)
        wan_links_frame.pack(fill=tk.X, padx=10, pady=10)

        self.wan_links_tree = ttk.Treeview(wan_links_frame, 
                                           columns=("Roteador", "Rede de Enlace", "IP WAN (Roteador)", "Gateway (ISP)"), 
                                           show="headings", height=4)
        
        self.wan_links_tree.heading("Roteador", text="Roteador")
        self.wan_links_tree.heading("Rede de Enlace", text="Rede de Enlace")
        self.wan_links_tree.heading("IP WAN (Roteador)", text="IP WAN (Roteador)")
        self.wan_links_tree.heading("Gateway (ISP)", text="Gateway (ISP)")

        self.wan_links_tree.column("Roteador", width=150)
        self.wan_links_tree.column("Rede de Enlace", width=150)
        self.wan_links_tree.column("IP WAN (Roteador)", width=150)
        self.wan_links_tree.column("Gateway (ISP)", width=150)

        self.wan_links_tree.pack(fill=tk.X, expand=True)

        # Frame para a tabela de roteamento
        routing_frame = ttk.LabelFrame(main_frame, text="Tabelas de Roteamento", padding=10)
        routing_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Frame para controles
        controls_frame = ttk.Frame(routing_frame)
        controls_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(controls_frame, text="Gerar Tabelas",
                   command=self.update_routing_table).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Checkbutton(controls_frame, text="Mostrar Roteamento de Saída (LAN->WAN)", 
                        variable=self.show_inter_router_routes, 
                        command=self.update_routing_table).pack(side=tk.LEFT, padx=5)

        ttk.Checkbutton(controls_frame, text="Mostrar Roteamento de Entrada (WAN->LAN)", 
                        variable=self.show_inbound_routes, 
                        command=self.update_routing_table).pack(side=tk.LEFT, padx=5)

        # Treeview para a tabela de roteamento
        self.routing_tree = ttk.Treeview(routing_frame, columns=("DEPT", "SRC", "DST", "GATEWAY"), show="headings")
        
        self.routing_tree.heading("DEPT", text="Descrição da Rota")
        self.routing_tree.heading("SRC", text="Rede de Origem")
        self.routing_tree.heading("DST", text="Rede de Destino")
        self.routing_tree.heading("GATEWAY", text="Gateway (Próximo Salto)")

        self.routing_tree.column("DEPT", width=300)
        self.routing_tree.column("SRC", width=180)
        self.routing_tree.column("DST", width=180)
        self.routing_tree.column("GATEWAY", width=150)

        self.routing_tree.pack(fill=tk.BOTH, expand=True)

    def update_routing_table(self):
        """Atualiza a tabela de roteamento com base nas redes adicionadas"""
        for item in self.wan_links_tree.get_children(): self.wan_links_tree.delete(item)
        for item in self.routing_tree.get_children(): self.routing_tree.delete(item)
            
        if not self.networks_data: return

        # 1. Gerar links WAN e preparar cores
        routers = sorted(list(set(net.get("Roteador", "Roteador Padrão") for net in self.networks_data)))
        wan_info, router_color_map = {}, {}
        current_wan_ip = ipaddress.ip_address('100.0.0.0')

        for i, router_name in enumerate(routers):
            color = self.router_colors[i % len(self.router_colors)]
            router_color_map[router_name] = color
            self.routing_tree.tag_configure(router_name, background=color)

            wan_network = ipaddress.ip_network(f"{current_wan_ip}/30")
            isp_gateway, router_wan_ip = wan_network.network_address + 1, wan_network.network_address + 2
            wan_info[router_name] = {'isp_gateway': isp_gateway}
            self.wan_links_tree.insert("", tk.END, values=(router_name, str(wan_network), str(router_wan_ip), str(isp_gateway)))
            current_wan_ip += 4

        # 2. Agrupar redes por roteador
        routers_data = {router_name: [] for router_name in routers}
        for net in self.networks_data:
            routers_data[net.get("Roteador", "Roteador Padrão")].append(net)

        # 3. Gerar tabelas
        for router_name in routers:
            networks = routers_data[router_name]
            color_tag = (router_name,)

            # Tabela Interna
            self.routing_tree.insert("", tk.END, values=(f"--- Tabela Interna: {router_name} ---", "", "", ""), tags=('header',))
            if len(networks) > 1:
                for src_net in networks:
                    for dst_net in networks:
                        if src_net == dst_net: continue
                        entry = (f"  (INT) {src_net['Nome Host']} -> {dst_net['Nome Host']}", f"{src_net['IP Rede']}/{src_net['Máscara']}", f"{dst_net['IP Rede']}/{dst_net['Máscara']}", dst_net['Gateway'])
                        self.routing_tree.insert("", tk.END, values=entry, tags=color_tag)

            # Tabela de Entrada (WAN->LAN)
            if self.show_inbound_routes.get() and len(routers) > 1:
                self.routing_tree.insert("", tk.END, values=(f"--- Tabela de Entrada (WAN->LAN): {router_name} ---", "", "", ""), tags=('header',))
                for ext_router_name, ext_networks in routers_data.items():
                    if router_name == ext_router_name: continue
                    for src_net in ext_networks:
                        for dst_net in networks:
                            entry = (f"  (IN) De {src_net['Nome Host']} ({ext_router_name}) Para {dst_net['Nome Host']}", f"{src_net['IP Rede']}/{src_net['Máscara']}", f"{dst_net['IP Rede']}/{dst_net['Máscara']}", dst_net['Gateway'])
                            self.routing_tree.insert("", tk.END, values=entry, tags=color_tag)

            # Tabela de Saída (LAN->WAN)
            if self.show_inter_router_routes.get() and len(routers) > 1:
                self.routing_tree.insert("", tk.END, values=(f"--- Tabela de Saída (LAN->WAN): {router_name} ---", "", "", ""), tags=('header',))
                src_gateway = wan_info[router_name]['isp_gateway']
                for src_net in networks:
                    for ext_router_name, ext_networks in routers_data.items():
                        if router_name == ext_router_name: continue
                        for dst_net in ext_networks:
                            entry = (f"  (OUT) De {src_net['Nome Host']} Para {dst_net['Nome Host']} ({ext_router_name})", f"{src_net['IP Rede']}/{src_net['Máscara']}", f"{dst_net['IP Rede']}/{dst_net['Máscara']}", str(src_gateway))
                            self.routing_tree.insert("", tk.END, values=entry, tags=color_tag)

        self.routing_tree.tag_configure('header', font=('Arial', 10, 'bold'), background='#ddd')

    def setup_input_frame(self, parent):
        """Configura o frame de entrada de dados"""
        input_frame = ttk.LabelFrame(parent, text="Entrada de Dados", padding=10)
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Grid para os campos de entrada
        fields_frame = ttk.Frame(input_frame)
        fields_frame.pack(fill=tk.X)
        
        # Campos de entrada
        ttk.Label(fields_frame, text="Nome do Host:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.host_entry = ttk.Entry(fields_frame, width=15)
        self.host_entry.grid(row=0, column=1, padx=(0, 10))
        
        ttk.Label(fields_frame, text="IP:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.ip_entry = ttk.Entry(fields_frame, width=15)
        self.ip_entry.grid(row=0, column=3, padx=(0, 10))
        
        ttk.Label(fields_frame, text="Máscara (/24 ou 255.255.255.0):").grid(row=0, column=4, sticky=tk.W, padx=(0, 5))
        self.mask_entry = ttk.Entry(fields_frame, width=15)
        self.mask_entry.grid(row=0, column=5, padx=(0, 10))
        
        ttk.Label(fields_frame, text="IP de Rede (opcional):").grid(row=0, column=6, sticky=tk.W, padx=(0, 5))
        self.network_entry = ttk.Entry(fields_frame, width=15)
        self.network_entry.grid(row=0, column=7, padx=(0, 10))
        
        ttk.Label(fields_frame, text="Roteador:").grid(row=0, column=8, sticky=tk.W, padx=(0, 5))
        self.router_entry = ttk.Entry(fields_frame, width=15)
        self.router_entry.grid(row=0, column=9, padx=(0, 10))
        
        # Botões
        button_frame = ttk.Frame(input_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="Calcular e Adicionar", 
                  command=self.add_network).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Limpar Campos", 
                  command=self.clear_fields).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Adicionar Exemplos", 
                  command=self.add_examples).pack(side=tk.LEFT)
    
    def setup_table_frame(self, parent):
        """Configura o frame da tabela estilo planilha"""
        table_frame = ttk.LabelFrame(parent, text="Resultados - Tabela de Redes", padding=5)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Frame para controles da tabela
        controls_frame = ttk.Frame(table_frame)
        controls_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Botão para mostrar/ocultar colunas binárias
        self.binary_columns_visible = False
        self.toggle_binary_btn = ttk.Button(controls_frame, text="Mostrar Colunas Binárias", 
                                          command=self.toggle_binary_columns)
        self.toggle_binary_btn.pack(side=tk.LEFT)
        
        # Configurar Treeview com scrollbars
        tree_frame = ttk.Frame(table_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Definir todas as colunas
        self.all_columns = (
            "Roteador", "Nome Host", "IP", "Máscara", "IP Rede", "Gateway", "Broadcast",
            "IP Binário", "Máscara Binária", "Binário de Rede", 
            "Nº Sub-Redes", "Intervalo Subredes", "Total IPs", "Hosts Utilizáveis"
        )
        
        # Colunas binárias que serão ocultadas por padrão
        self.binary_columns = ("IP Binário", "Máscara Binária", "Binário de Rede")
        
        # Colunas visíveis inicialmente (sem as binárias)
        self.visible_columns = tuple(col for col in self.all_columns if col not in self.binary_columns)
        
        self.tree = ttk.Treeview(tree_frame, columns=self.all_columns, show="headings", height=15)
        
        # Configurar cabeçalhos e larguras das colunas
        self.column_widths = {
            "Roteador": 100,
            "Nome Host": 100,
            "IP": 100,
            "Máscara": 120,
            "IP Rede": 100,
            "Gateway": 100,
            "Broadcast": 100,
            "IP Binário": 200,
            "Máscara Binária": 200,
            "Binário de Rede": 200,
            "Nº Sub-Redes": 80,
            "Intervalo Subredes": 150,
            "Total IPs": 80,
            "Hosts Utilizáveis": 100
        }
        
        for col in self.all_columns:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_by_column(c))
            self.tree.column(col, width=self.column_widths.get(col, 100), minwidth=50)
        
        # Ocultar colunas binárias inicialmente
        self.tree["displaycolumns"] = self.visible_columns
        
        # Frame para scrollbars
        scrollbar_frame = ttk.Frame(tree_frame)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout for better scrollbars positioning
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        # Bind para seleção
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        self.tree.bind("<Double-1>", self.edit_selected_row)
    
    def setup_action_frame(self, parent):
        """Configura o frame de ações"""
        action_frame = ttk.LabelFrame(parent, text="Ações", padding=10)
        action_frame.pack(fill=tk.X)
        
        # Primeira linha de botões
        row1_frame = ttk.Frame(action_frame)
        row1_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(row1_frame, text="Remover Selecionado", 
                  command=self.remove_selected).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(row1_frame, text="Editar Selecionado", 
                  command=self.edit_selected_row).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(row1_frame, text="Limpar Tabela", 
                  command=self.clear_table).pack(side=tk.LEFT, padx=(0, 5))
        
        # Segunda linha de botões
        row2_frame = ttk.Frame(action_frame)
        row2_frame.pack(fill=tk.X)
        
        ttk.Button(row2_frame, text="Exportar CSV", 
                  command=self.export_csv).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(row2_frame, text="Exportar TXT", 
                  command=self.export_txt).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(row2_frame, text="Importar CSV", 
                  command=self.import_csv).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(row2_frame, text="Salvar Projeto", 
                  command=self.save_project).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(row2_frame, text="Carregar Projeto", 
                  command=self.load_project).pack(side=tk.LEFT)
    
    def add_network(self):
        """Adiciona uma nova rede à tabela"""
        try:
            # Obter dados dos campos
            host_name = self.host_entry.get().strip()
            ip = self.ip_entry.get().strip()
            mask = self.mask_entry.get().strip()
            network_ip = self.network_entry.get().strip() or None
            router = self.router_entry.get().strip()
            
            if not all([host_name, ip, mask]):
                messagebox.showerror("Erro", "Preencha pelo menos Nome do Host, IP e Máscara!")
                return
            
            # Normalizar a máscara (aceita CIDR ou formato tradicional)
            try:
                normalized_mask = self.normalize_mask(mask)
            except ValueError as e:
                messagebox.showerror("Erro", str(e))
                return
            
            # Calcular usando a classe NetworkCalculator
            result = self.calculator.process_network_entry(host_name, ip, normalized_mask, network_ip)
            result['Roteador'] = router
            
            # Adicionar à tabela
            values = (
                result['Roteador'],
                result['Nome Host'],
                result['IP'],
                result['Máscara'],
                result['IP Rede'],
                result['Gateway'],
                result.get('Broadcast', ''),
                result['IP Binario'],
                result['Mascara Binaria'],
                result['Binario de Rede'],
                result['Numero de Sub-Redes'],
                result['Intervalo de Subredes'],
                result['Total de IPs'],
                result['Hosts Utilizaveis']
            )
            
            self.tree.insert("", tk.END, values=values)
            self.networks_data.append(result)
            
            # Limpar campos após adicionar
            self.clear_fields()
            
            messagebox.showinfo("Sucesso", "Rede adicionada com sucesso!")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao processar rede: {str(e)}")
    
    def clear_fields(self):
        """Limpa os campos de entrada"""
        self.host_entry.delete(0, tk.END)
        self.ip_entry.delete(0, tk.END)
        self.mask_entry.delete(0, tk.END)
        self.network_entry.delete(0, tk.END)
        self.router_entry.delete(0, tk.END)
    
    def add_examples(self):
        """Adiciona exemplos de redes"""
        examples = [
            ("Roteador-A", "Vendas", "10.0.16.0", "22", "10.0.16.0"),
            ("Roteador-A", "Produção", "10.0.0.0", "/21", "10.0.0.0"),
            ("Roteador-B", "Fiscal", "172.16.0.0", "/26", "172.16.0.0"),
            ("Roteador-B", "Expedição", "172.16.0.64", "/26", "172.16.0.64")
        ]
        
        try:
            for router, host_name, ip, mask, network_ip in examples:
                normalized_mask = self.normalize_mask(mask)
                result = self.calculator.process_network_entry(host_name, ip, normalized_mask, network_ip)
                result['Roteador'] = router
                
                values = (
                    result['Roteador'],
                    result['Nome Host'],
                    result['IP'],
                    result['Máscara'],
                    result['IP Rede'],
                    result['Gateway'],
                    result.get('Broadcast', ''),
                    result['IP Binario'],
                    result['Mascara Binaria'],
                    result['Binario de Rede'],
                    result['Numero de Sub-Redes'],
                    result['Intervalo de Subredes'],
                    result['Total de IPs'],
                    result['Hosts Utilizaveis']
                )
                
                self.tree.insert("", tk.END, values=values)
                self.networks_data.append(result)
            
            messagebox.showinfo("Sucesso", "Exemplos adicionados com sucesso!")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao adicionar exemplos: {str(e)}")
    
    def remove_selected(self):
        """Remove o item selecionado da tabela"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um item para remover!")
            return
        
        if messagebox.askyesno("Confirmar", "Deseja remover o item selecionado?"):
            for item in selected:
                index = self.tree.index(item)
                self.tree.delete(item)
                if 0 <= index < len(self.networks_data):
                    del self.networks_data[index]
    
    def clear_table(self):
        """Limpa toda a tabela"""
        if messagebox.askyesno("Confirmar", "Deseja limpar toda a tabela?"):
            for item in self.tree.get_children():
                self.tree.delete(item)
            self.networks_data.clear()
    
    def on_tree_select(self, event):
        """Callback para seleção na tabela"""
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            values = item['values']
            
            self.clear_fields()

            if len(values) > 4:
                self.router_entry.insert(0, values[0])
                self.host_entry.insert(0, values[1])
                self.ip_entry.insert(0, values[2])
                self.mask_entry.insert(0, values[3])
                self.network_entry.insert(0, values[4])
    
    def edit_selected_row(self, event=None):
        """Permite editar a linha selecionada"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um item para editar!")
            return
        
        self.on_tree_select(None)

        if messagebox.askyesno("Editar", "Os campos foram preenchidos com os dados selecionados.\nDeseja substituir este item pelos novos dados?"):
            item = selected[0]
            index = self.tree.index(item)
            self.tree.delete(item)
            if 0 <= index < len(self.networks_data):
                del self.networks_data[index]
            
            self.add_network()
    
    def cidr_to_netmask(self, cidr):
        """Converte notação CIDR para máscara de sub-rede"""
        if isinstance(cidr, str) and cidr.startswith('/'):
            cidr = cidr[1:]
        
        try:
            cidr_int = int(cidr)
            if not 0 <= cidr_int <= 32:
                raise ValueError("CIDR deve estar entre 0 e 32")
            
            mask_bits = '1' * cidr_int + '0' * (32 - cidr_int)
            
            octets = []
            for i in range(0, 32, 8):
                octet_bits = mask_bits[i:i+8]
                octets.append(str(int(octet_bits, 2)))
            
            return '.'.join(octets)
        except ValueError:
            raise ValueError(f"Formato CIDR inválido: /{cidr}")
    
    def normalize_mask(self, mask):
        """Normaliza a máscara de entrada (aceita CIDR ou formato tradicional)"""
        mask = mask.strip()
        
        if mask.startswith('/') or mask.isdigit():
            return self.cidr_to_netmask(mask)
        
        try:
            ipaddress.IPv4Address(mask)
            return mask
        except ipaddress.AddressValueError:
            raise ValueError(f"Máscara inválida: {mask}")
    
    def toggle_binary_columns(self):
        """Alterna a visibilidade das colunas binárias"""
        if self.binary_columns_visible:
            self.tree["displaycolumns"] = self.visible_columns
            self.toggle_binary_btn.config(text="Mostrar Colunas Binárias")
            self.binary_columns_visible = False
        else:
            self.tree["displaycolumns"] = self.all_columns
            self.toggle_binary_btn.config(text="Ocultar Colunas Binárias")
            self.binary_columns_visible = True
    
    def sort_by_column(self, col):
        """Ordena a tabela por coluna"""
        data = [(self.tree.set(item, col), item) for item in self.tree.get_children()]
        
        try:
            data.sort(key=lambda x: float(x[0].replace('.', '').replace('-', '').replace(' ', '')[:10]))
        except:
            data.sort()
        
        for index, (val, item) in enumerate(data):
            self.tree.move(item, '', index)
    
    def export_csv(self):
        """Exporta dados para CSV"""
        try:
            if not self.networks_data:
                messagebox.showwarning("Aviso", "Não há dados para exportar!")
                return
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Salvar como CSV"
            )
            
            if filename:
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    fieldnames = list(self.networks_data[0].keys())
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    
                    writer.writeheader()
                    for network in self.networks_data:
                        writer.writerow(network)
                
                messagebox.showinfo("Sucesso", f"Dados exportados para {filename}")
        
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar CSV: {str(e)}")
    
    def export_txt(self):
        """Exporta dados para TXT formatado"""
        try:
            if not self.networks_data:
                messagebox.showwarning("Aviso", "Não há dados para exportar!")
                return
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                title="Salvar como TXT"
            )
            
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write("CALCULADORA DE REDES - RELATÓRIO\n")
                    f.write("="*80 + "\n")
                    f.write(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                    f.write(f"Total de redes: {len(self.networks_data)}\n\n")
                    
                    headers = list(self.networks_data[0].keys())
                    
                    col_widths = {}
                    for header in headers:
                        col_widths[header] = max(len(header), 
                                               max(len(str(network.get(header, ''))) for network in self.networks_data))
                    
                    header_line = " | ".join(header.ljust(col_widths[header]) for header in headers)
                    f.write(header_line + "\n")
                    f.write("-" * len(header_line) + "\n")
                    
                    for network in self.networks_data:
                        row = " | ".join(str(network.get(header, '')).ljust(col_widths[header]) for header in headers)
                        f.write(row + "\n")
                    
                    f.write("\n" + "="*80)
                
                messagebox.showinfo("Sucesso", f"Dados exportados para {filename}")
        
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar TXT: {str(e)}")
    
    def import_csv(self):
        """Importa dados de CSV"""
        try:
            filename = filedialog.askopenfilename(
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Importar CSV"
            )
            
            if filename:
                with open(filename, 'r', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile)
                    imported_count = 0
                    
                    for row in reader:
                        if 'Nome Host' in row and 'IP' in row and 'Máscara' in row:
                            values = (
                                row.get('Roteador', ''),
                                row.get('Nome Host', ''),
                                row.get('IP', ''),
                                row.get('Máscara', ''),
                                row.get('IP Rede', ''),
                                row.get('Gateway', ''),
                                row.get('Broadcast', ''),
                                row.get('IP Binario', ''),
                                row.get('Mascara Binaria', ''),
                                row.get('Binario de Rede', ''),
                                row.get('Numero de Sub-Redes', ''),
                                row.get('Intervalo de Subredes', ''),
                                row.get('Total de IPs', ''),
                                row.get('Hosts Utilizaveis', '')
                            )
                            
                            self.tree.insert("", tk.END, values=values)
                            self.networks_data.append(dict(row))
                            imported_count += 1
                
                messagebox.showinfo("Sucesso", f"{imported_count} redes importadas de {filename}")
        
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao importar CSV: {str(e)}")
    
    def save_project(self):
        """Salva projeto em JSON"""
        try:
            if not self.networks_data:
                messagebox.showwarning("Aviso", "Não há dados para salvar!")
                return
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Salvar Projeto"
            )
            
            if filename:
                project_data = {
                    'created': datetime.now().isoformat(),
                    'networks': self.networks_data
                }
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(project_data, f, indent=2, ensure_ascii=False)
                
                messagebox.showinfo("Sucesso", f"Projeto salvo em {filename}")
        
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar projeto: {str(e)}")
    
    def load_project(self):
        """Carrega projeto de JSON"""
        try:
            filename = filedialog.askopenfilename(
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Carregar Projeto"
            )
            
            if filename:
                with open(filename, 'r', encoding='utf-8') as f:
                    project_data = json.load(f)
                
                if 'networks' in project_data:
                    self.clear_table()
                    
                    for network in project_data['networks']:
                        values = (
                            network.get('Roteador', ''),
                            network.get('Nome Host', ''),
                            network.get('IP', ''),
                            network.get('Máscara', ''),
                            network.get('IP Rede', ''),
                            network.get('Gateway', ''),
                            network.get('Broadcast', ''),
                            network.get('IP Binario', ''),
                            network.get('Mascara Binaria', ''),
                            network.get('Binario de Rede', ''),
                            network.get('Numero de Sub-Redes', ''),
                            network.get('Intervalo de Subredes', ''),
                            network.get('Total de IPs', ''),
                            network.get('Hosts Utilizaveis', '')
                        )
                        
                        self.tree.insert("", tk.END, values=values)
                        self.networks_data.append(network)
                    
                    messagebox.showinfo("Sucesso", f"Projeto carregado de {filename}")
                else:
                    messagebox.showerror("Erro", "Arquivo de projeto inválido!")
        
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar projeto: {str(e)}")
    
    def run(self):
        """Executa a aplicação"""
        self.root.mainloop()

if __name__ == "__main__":
    app = NetworkCalculatorGUI()
    app.run()