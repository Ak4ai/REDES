import ipaddress
import math

class NetworkCalculator:
    def __init__(self):
        pass
    
    def ip_to_binary(self, ip):
        """Converte IP para formato binário com pontos"""
        octets = ip.split('.')
        binary_octets = []
        for octet in octets:
            binary_octets.append(format(int(octet), '08b'))
        return '.'.join(binary_octets)
    
    def mask_to_binary(self, mask):
        """Converte máscara para formato binário com pontos"""
        return self.ip_to_binary(mask)
    
    def calculate_network_ip(self, ip, mask):
        """Calcula o IP de rede"""
        network = ipaddress.IPv4Network(f"{ip}/{mask}", strict=False)
        return str(network.network_address)
    
    def calculate_gateway(self, network_ip, mask):
        """Calcula o gateway (primeiro IP válido da rede)"""
        network = ipaddress.IPv4Network(f"{network_ip}/{mask}", strict=False)
        # Gateway é normalmente o primeiro IP utilizável da rede
        first_usable = network.network_address + 1
        return str(first_usable)
    
    def calculate_broadcast(self, network_ip, mask):
        """Calcula o endereço de broadcast da rede"""
        network = ipaddress.IPv4Network(f"{network_ip}/{mask}", strict=False)
        return str(network.broadcast_address)
    
    def calculate_subnet_count(self, mask):
        """Calcula o número de sub-redes possíveis"""
        # Converte máscara para CIDR
        mask_int = sum([bin(int(octet)).count('1') for octet in mask.split('.')])
        
        # Para uma rede classe A (10.x.x.x), assumindo /8 como padrão
        # Para uma rede classe B (172.16.x.x), assumindo /16 como padrão  
        # Para uma rede classe C (192.168.x.x), assumindo /24 como padrão
        
        # Determina a classe da rede baseada no primeiro octeto
        if mask.startswith('255.0') or mask == '255.0.0.0':
            default_mask = 8
        elif mask.startswith('255.255.0') or mask == '255.255.0.0':
            default_mask = 16
        elif mask.startswith('255.255.255') or mask == '255.255.255.0':
            default_mask = 24
        else:
            # Calcula baseado na máscara atual
            if mask_int <= 8:
                default_mask = 8
            elif mask_int <= 16:
                default_mask = 16
            elif mask_int <= 24:
                default_mask = 24
            else:
                default_mask = 24
        
        subnet_bits = mask_int - default_mask
        if subnet_bits <= 0:
            return 1
        
        return 2 ** subnet_bits
    
    def calculate_subnet_range(self, network_ip, mask):
        """Calcula o intervalo de IPs da sub-rede"""
        network = ipaddress.IPv4Network(f"{network_ip}/{mask}", strict=False)
        
        # IP inicial da rede
        start_ip = network.network_address
        
        # IP final da rede (broadcast)
        end_ip = network.broadcast_address
        
        return f"{start_ip} - {end_ip}"
    
    def calculate_host_count(self, mask):
        """Calcula o número de hosts possíveis na rede"""
        # Converte máscara para CIDR
        mask_int = sum([bin(int(octet)).count('1') for octet in mask.split('.')])
        
        # Número de bits para hosts
        host_bits = 32 - mask_int
        
        # Número total de IPs possíveis
        total_ips = 2 ** host_bits
        
        # Número de hosts utilizáveis (subtrai network address e broadcast address)
        usable_hosts = total_ips - 2 if total_ips > 2 else 0
        
        return {
            'total_ips': total_ips,
            'usable_hosts': usable_hosts
        }
    
    def process_network_entry(self, host_name, ip, mask, network_ip=None):
        """Processa uma entrada de rede e calcula todos os campos"""
        
        # Se network_ip não foi fornecido, calcula
        if not network_ip:
            network_ip = self.calculate_network_ip(ip, mask)
        
        # Calcula gateway
        gateway = self.calculate_gateway(network_ip, mask)
        
        # Calcula broadcast
        broadcast = self.calculate_broadcast(network_ip, mask)
        
        # Converte IPs para binário
        ip_binary = self.ip_to_binary(ip)
        mask_binary = self.mask_to_binary(mask)
        network_binary = self.ip_to_binary(network_ip)
        
        # Calcula número de sub-redes
        subnet_count = self.calculate_subnet_count(mask)
        
        # Calcula intervalo de sub-redes
        subnet_range = self.calculate_subnet_range(network_ip, mask)
        
        # Calcula número de hosts possíveis
        host_info = self.calculate_host_count(mask)
        
        return {
            'Nome Host': host_name,
            'IP': ip,
            'Máscara': mask,
            'IP Rede': network_ip,
            'Gateway': gateway,
            'Broadcast': broadcast,
            'IP Binario': ip_binary,
            'Mascara Binaria': mask_binary,
            'Binario de Rede': network_binary,
            'Numero de Sub-Redes': subnet_count,
            'Intervalo de Subredes': subnet_range,
            'Total de IPs': host_info['total_ips'],
            'Hosts Utilizaveis': host_info['usable_hosts']
        }

def main():
    calculator = NetworkCalculator()
    
    print("=== CALCULADORA DE REDES ===\n")
    print("Preencha as informações básicas e o programa calculará os demais campos.\n")
    
    # Lista para armazenar todas as entradas
    networks = []
    
    while True:
        print("\n--- Nova Entrada de Rede ---")
        
        # Entrada dos dados básicos
        host_name = input("Nome do Host: ").strip()
        if not host_name:
            break
            
        ip = input("IP: ").strip()
        mask = input("Máscara: ").strip()
        network_ip = input("IP de Rede (deixe vazio para calcular automaticamente): ").strip()
        
        if not network_ip:
            network_ip = None
        
        try:
            # Processa a entrada
            result = calculator.process_network_entry(host_name, ip, mask, network_ip)
            networks.append(result)
            
            print("\n--- Resultado Calculado ---")
            for key, value in result.items():
                print(f"{key}: {value}")
                
        except Exception as e:
            print(f"Erro ao processar entrada: {e}")
            continue
        
        # Pergunta se deseja continuar
        continue_input = input("\nDeseja adicionar outra entrada? (s/n): ").strip().lower()
        if continue_input not in ['s', 'sim', 'y', 'yes']:
            break
    
    # Exibe tabela final
    if networks:
        print("\n" + "="*150)
        print("TABELA FINAL DE REDES")
        print("="*150)
        
        # Cabeçalho
        headers = ['Nome Host', 'IP', 'Máscara', 'IP Rede', 'Gateway', 'IP Binario', 
                  'Mascara Binaria', 'Binario de Rede', 'Numero de Sub-Redes', 'Intervalo de Subredes',
                  'Total de IPs', 'Hosts Utilizaveis']
        
        # Calcula larguras das colunas
        col_widths = {}
        for header in headers:
            col_widths[header] = max(len(header), 
                                   max(len(str(network.get(header, ''))) for network in networks))
        
        # Imprime cabeçalho
        header_line = " | ".join(header.ljust(col_widths[header]) for header in headers)
        print(header_line)
        print("-" * len(header_line))
        
        # Imprime dados
        for network in networks:
            row = " | ".join(str(network.get(header, '')).ljust(col_widths[header]) for header in headers)
            print(row)
        
        print("="*150)
        
        # Opção para salvar em arquivo
        save_option = input("\nDeseja salvar os resultados em um arquivo? (s/n): ").strip().lower()
        if save_option in ['s', 'sim', 'y', 'yes']:
            filename = input("Nome do arquivo (sem extensão): ").strip()
            if not filename:
                filename = "redes_calculadas"
            
            save_to_file(networks, filename)

def save_to_file(networks, filename):
    """Salva os resultados em arquivo de texto"""
    try:
        with open(f"{filename}.txt", "w", encoding="utf-8") as f:
            f.write("TABELA DE REDES CALCULADAS\n")
            f.write("="*150 + "\n\n")
            
            headers = ['Nome Host', 'IP', 'Máscara', 'IP Rede', 'Gateway', 'IP Binario', 
                      'Mascara Binaria', 'Binario de Rede', 'Numero de Sub-Redes', 'Intervalo de Subredes',
                      'Total de IPs', 'Hosts Utilizaveis']
            
            # Calcula larguras das colunas
            col_widths = {}
            for header in headers:
                col_widths[header] = max(len(header), 
                                       max(len(str(network.get(header, ''))) for network in networks))
            
            # Escreve cabeçalho
            header_line = " | ".join(header.ljust(col_widths[header]) for header in headers)
            f.write(header_line + "\n")
            f.write("-" * len(header_line) + "\n")
            
            # Escreve dados
            for network in networks:
                row = " | ".join(str(network.get(header, '')).ljust(col_widths[header]) for header in headers)
                f.write(row + "\n")
            
            f.write("\n" + "="*150)
        
        print(f"Arquivo '{filename}.txt' salvo com sucesso!")
        
    except Exception as e:
        print(f"Erro ao salvar arquivo: {e}")

def test_examples():
    """Testa com os exemplos fornecidos"""
    calculator = NetworkCalculator()
    
    examples = [
        ("Host teste", "10.0.0.0", "255.255.255.0", "10.0.0.0"),
        ("Host teste", "10.0.0.0", "255.255.255.128", "10.0.0.0"),
        ("Host teste", "172.16.0.62", "255.255.255.192", "172.16.0.0"),
        ("Almoxarifado", "10.0.20.0", "255.255.255.240", "10.0.20.0"),
        ("Vendas", "10.0.16.0", "255.255.252.0", "10.0.16.0"),
        ("Terceirizados", "10.0.0.0", "255.255.240.0", "10.0.0.0")
    ]
    
    print("=== TESTE COM EXEMPLOS ===\n")
    
    for host_name, ip, mask, network_ip in examples:
        result = calculator.process_network_entry(host_name, ip, mask, network_ip)
        
        print(f"Host: {host_name}")
        for key, value in result.items():
            print(f"  {key}: {value}")
        print()

if __name__ == "__main__":
    # Pergunta se deseja testar com exemplos ou usar modo interativo
    print("Escolha uma opção:")
    print("1 - Modo interativo (inserir dados manualmente)")
    print("2 - Testar com exemplos fornecidos")
    
    choice = input("Opção (1 ou 2): ").strip()
    
    if choice == "2":
        test_examples()
    else:
        main()