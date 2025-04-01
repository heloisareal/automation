import paramiko
import tkinter as tk
from tkinter import messagebox
import threading
import time
import datetime
import os

# Credenciais corretas para login inicial
correct_username = 'heloreal'
correct_password = 'real'

# Valores padrão para a conexão SSH
default_usr = "secadmin"
default_pass = "Infinera2!"
default_port = 22
default_ip = "192.168.144.234"

# Lista de IPs conectados (simulando um estado com múltiplos dispositivos conectados)
connected_ips = []

# Variáveis globais para o SSH e para a interface
ssh_client = None
hostname = None

def limpar_arquivos():
    """Função para limpar os arquivos na pasta 'outputs'."""
    outputs_dir = 'outputs'
    
    # Verifica se a pasta outputs existe
    if os.path.exists(outputs_dir):
        # Percorre todos os itens dentro da pasta outputs
        for filename in os.listdir(outputs_dir):
            file_path = os.path.join(outputs_dir, filename)
            try:
                # Verifica se é um arquivo e não uma subpasta
                if os.path.isfile(file_path):
                    os.remove(file_path)  # Remove o arquivo
                    print(f"Arquivo {filename} apagado.")
                # Caso queira remover diretórios vazios, pode incluir a parte abaixo
                elif os.path.isdir(file_path) and not os.listdir(file_path):  # Verifica se o diretório está vazio
                    os.rmdir(file_path)  # Remove o diretório vazio
                    print(f"Pasta {filename} apagada.")
            except Exception as e:
                print(f"Erro ao apagar o arquivo {filename}: {e}")

def login():
    """Verifica o usuário e senha e abre a janela de conexão SSH após login."""
    user = username_entry.get()
    pwd = password_entry.get()

    if user == correct_username and pwd == correct_password:
        login_window.destroy()  # Fecha a janela de login
        connection_window()  # Abre a janela de conexão SSH
    else:
        messagebox.showerror("Erro", "Usuário ou senha inválidos.")

def connection_window():
    """Cria a janela para inserir detalhes da conexão SSH."""
    global hostname_entry, port_entry, username_entry, password_entry, output_text, ssh_client

    conn_window = tk.Tk()
    conn_window.title("Detalhes da Conexão SSH")
    conn_window.geometry("500x400")
    conn_window.config(bg="#1e3a5f")  # Cor de fundo azul, estilo Nokia

    # Labels e campos de entrada para informações de conexão
    tk.Label(conn_window, text="Hostname:", bg="#1e3a5f", fg="white", font=("Nokia Sans", 12)).grid(row=0, column=0, padx=10, pady=5, sticky='w')
    hostname_entry = tk.Entry(conn_window, font=("Nokia Sans", 12))
    hostname_entry.grid(row=0, column=1, padx=10, pady=5, sticky='w')
    hostname_entry.insert(0, default_ip)

    tk.Label(conn_window, text="Porta:", bg="#1e3a5f", fg="white", font=("Nokia Sans", 12)).grid(row=1, column=0, padx=10, pady=5, sticky='w')
    port_entry = tk.Entry(conn_window, font=("Nokia Sans", 12))
    port_entry.grid(row=1, column=1, padx=10, pady=5, sticky='w')
    port_entry.insert(0, default_port)

    tk.Label(conn_window, text="Usuário:", bg="#1e3a5f", fg="white", font=("Nokia Sans", 12)).grid(row=2, column=0, padx=10, pady=5, sticky='w')
    username_entry = tk.Entry(conn_window, font=("Nokia Sans", 12))
    username_entry.grid(row=2, column=1, padx=10, pady=5, sticky='w')
    username_entry.insert(0, default_usr)

    tk.Label(conn_window, text="Senha:", bg="#1e3a5f", fg="white", font=("Nokia Sans", 12)).grid(row=3, column=0, padx=10, pady=5, sticky='w')
    password_entry = tk.Entry(conn_window, show='*', font=("Nokia Sans", 12))
    password_entry.grid(row=3, column=1, padx=10, pady=5, sticky='w')
    password_entry.insert(0, default_pass)

    # Botão para estabelecer conexão SSH
    connect_button = tk.Button(conn_window, text="Conectar ao SSH", font=("Nokia Sans", 12), command=connect_ssh, bg="#005e9a", fg="white", padx=10, pady=5, relief="solid")
    connect_button.grid(row=4, columnspan=2, pady=15)

    # Caixa de texto para mostrar a saída da conexão
    output_text = tk.Text(conn_window, width=60, height=10, font=("Courier", 12), wrap="word", bg="#f7f7f7", bd=2, relief="sunken")
    output_text.grid(row=5, columnspan=2, padx=10, pady=10)

    # Definindo a função para desconectar ao fechar a janela
    def on_close():
        """Desconecta a sessão SSH quando a janela for fechada."""
        disconnect_ssh()
        conn_window.destroy()

    # Associando o evento de fechamento da janela com a função on_close
    conn_window.protocol("WM_DELETE_WINDOW", on_close)

    # Adicionando o binding para o pressionamento da tecla "Enter" para o botão de conexão
    conn_window.bind("<Return>", lambda event: connect_ssh())

    conn_window.mainloop()

def connect_ssh():
    """Estabelece a conexão SSH e abre a próxima janela."""
    global ssh_client, hostname
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    hostname = hostname_entry.get()
    port = int(port_entry.get())
    username = username_entry.get()
    password = password_entry.get()

    try:
        output_text.delete(1.0, tk.END)
        output_text.insert(tk.END, f"Conectando a {hostname} na porta {port}...\n")

        ssh_client.connect(hostname, port, username, password, timeout=10)
        output_text.insert(tk.END, "Conexão bem-sucedida!\n")

        # Adiciona o IP à lista de IPs conectados (apenas para o exemplo)
        connected_ips.append(hostname)
        show_connection_details(hostname, port)

    except paramiko.AuthenticationException:
        messagebox.showerror("Erro", "Falha na autenticação. Verifique suas credenciais.")
    except paramiko.SSHException as sshException:
        messagebox.showerror("Erro", f"Não foi possível estabelecer a conexão SSH: {sshException}")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao conectar: {e}")

def disconnect_ssh():
    """Desconecta a sessão SSH se estiver ativa."""
    global ssh_client
    if ssh_client.get_transport() is not None and ssh_client.get_transport().is_active():
        ssh_client.close()
        print("Sessão SSH desconectada.")
    else:
        print("Nenhuma sessão SSH ativa para desconectar.")

def show_connection_details(hostname, port):
    """Exibe os detalhes da conexão em uma nova janela."""
    details_window = tk.Tk()
    details_window.title("Detalhes da Conexão")
    details_window.geometry("500x400")
    details_window.config(bg="#1e3a5f")  # Cor de fundo azul, estilo Nokia

    tk.Label(details_window, text=f"Conectado a: {hostname}", bg="#1e3a5f", fg="white", font=("Nokia Sans", 12)).pack(pady=5)
    tk.Label(details_window, text=f"Porta: {port}", bg="#1e3a5f", fg="white", font=("Nokia Sans", 12)).pack(pady=5)

    execute_button = tk.Button(details_window, text="Executar Comandos", font=("Nokia Sans", 12), command=lambda: execute_command_from_file(details_window), bg="#005e9a", fg="white", padx=10, pady=5, relief="solid")
    execute_button.pack(pady=20)

    command_output_text = tk.Text(details_window, width=60, height=15, font=("Courier", 12), wrap="word", bg="#f7f7f7", bd=2, relief="sunken")
    command_output_text.pack(padx=10, pady=10)

    details_window.command_output_text = command_output_text

    details_window.mainloop()

def execute_command_from_file(details_window):
    """Executa os comandos do arquivo 'comandos.txt' e exibe a saída."""
    def run_command():
        try:
            # Verifica se o arquivo 'comandos.txt' existe
            if not os.path.exists('comandos.txt'):
                messagebox.showerror("Erro", "Arquivo 'comandos.txt' não encontrado.")
                return

            with open('comandos.txt', 'r') as file:
                commands = file.readlines()

            details_window.command_output_text.delete(1.0, tk.END)
            details_window.command_output_text.insert(tk.END, f"Executando comandos...\n")

            # Cria um shell e executa os comandos um por um
            shell = ssh_client.invoke_shell()

            for command in commands:
                command = command.strip()  # Remove espaços extras
                if command:  # Verifica se o comando não está vazio
                    shell.send(command + "\n")
                    time.sleep(1)  # Aguardar o comando ser processado

                    output = shell.recv(65535).decode()
                    details_window.command_output_text.insert(tk.END, f"\nComando: {command}\n")
                    details_window.command_output_text.insert(tk.END, output)

            # Verifica se a pasta 'outputs' existe, se não, cria
            if not os.path.exists('outputs'):
                os.makedirs('outputs')

            # Salva a saída em um arquivo com o nome do IP dentro da pasta 'outputs'
            output_file_name = f"outputs/{hostname}.txt"  # Salvando apenas com o nome do IP (hostname)
            with open(output_file_name, "w") as file:
                file.write(details_window.command_output_text.get(1.0, tk.END))

        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro: {e}")

    threading.Thread(target=run_command, daemon=True).start()

# Limpeza inicial dos arquivos na pasta outputs
limpar_arquivos()

# Criação da janela de login
login_window = tk.Tk()
login_window.title("Login")
login_window.geometry("400x250")  # Ajustando tamanho da janela de login
login_window.config(bg="#1e3a5f")  # Cor de fundo azul, estilo Nokia

# Campos de entrada para usuário e senha
tk.Label(login_window, text="Usuário:", bg="#1e3a5f", fg="white", font=("Nokia Sans", 12)).pack(pady=5)
username_entry = tk.Entry(login_window, font=("Nokia Sans", 12))
username_entry.pack(pady=5)

tk.Label(login_window, text="Senha:", bg="#1e3a5f", fg="white", font=("Nokia Sans", 12)).pack(pady=5)
password_entry = tk.Entry(login_window, show='*', font=("Nokia Sans", 12))
password_entry.pack(pady=5)

# Botão de login
login_button = tk.Button(login_window, text="Login", font=("Nokia Sans", 12), command=login, bg="#005e9a", fg="white", padx=10, pady=5, relief="solid")
login_button.pack(pady=10)

# Adicionando o binding para o pressionamento da tecla "Enter" para o botão de login
login_window.bind("<Return>", lambda event: login())

login_window.mainloop()
