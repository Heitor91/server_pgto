using System.Windows.Forms;
using System.Data;
using Microsoft.AspNetCore.SignalR.Client;
using ExcelDataReader;
using System.Collections.Generic;
using System.Diagnostics;
using System.Text.Json;
using System.Threading.Tasks;
using System.Text;

namespace interface_pgto
{
    public partial class Form1 : Form
    {
        private Dictionary<string, List<string>> empresaRelacionada = new();
        bool runApiPgtoControl = false;
        bool runApiBankControl = false;
        bool pgtoErpEnable = true;
        private Process pgtoProcess;
        private Process bankProcess;
        private Process aspnetProcess;
        private TextBox outputTextBox;
        private Button buttonApiPgto;
        private Button buttonApiBank;
        private Button buttonCtr;
        private static HttpClient client = new();

        public Form1()
        {
            InitializeComponent();
            IniciarServidorSignalR();
            System.Text.Encoding.RegisterProvider(System.Text.CodePagesEncodingProvider.Instance);
            SetupForm();
            CarregarDadosExcel();
            this.FormClosing += StopAspNetServer;
        }
        public async Task TestarConexao() {
            try 
            { 
                AdicionaLog("Tentando porta 7246"); 
                await IniciarSignalR(7246); 
            } 
            catch (Exception ex) 
            { 
                AdicionaLog($"Erro porta 7246: {ex.Message}"); 
                try 
                { 
                    AdicionaLog("Tentando porta 5061"); 
                    await IniciarSignalR(5061); 
                } 
                catch (Exception ex2) 
                { 
                    AdicionaLog($"Erro porta 5061: {ex2.Message}"); 
                } 
            } 
        }
        private void IniciarServidorSignalR()
        {
            try
            {
                // Cria um processo para iniciar o servidor ASP.NET
                ProcessStartInfo startInfo = new()
                {
                    FileName = "dotnet", // O comando "dotnet" é usado para executar o projeto ASP.NET
                    Arguments = "run --project C:\\Users\\heit_\\Documents\\USCS\\TCC\\server_pgto\\ServidorSignalR",
                    UseShellExecute = false,
                    CreateNoWindow = false
                };

                aspnetProcess = new() 
                { 
                    StartInfo = startInfo,
                    EnableRaisingEvents = true
                };
                aspnetProcess.OutputDataReceived += (sender, e) => Console.WriteLine(e.Data); 
                aspnetProcess.ErrorDataReceived += (sender, e) => Console.WriteLine(e.Data);
                aspnetProcess.Start();
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Erro ao iniciar o servidor SignalR: {ex.Message}");
            }
        }
        private void CarregarDadosExcel()
        {
            try
            {
                string caminhoArquivoExcel = @"C:\Users\heit_\Documents\USCS\TCC\referencias.xlsx";
                using var stream = File.Open(caminhoArquivoExcel, FileMode.Open, FileAccess.Read);
                using var reader = ExcelReaderFactory.CreateReader(stream);

                DataSet result = reader.AsDataSet();

                // Verificação para garantir que as tabelas existem antes de carregá-las
                if (result.Tables.Contains("referencias"))
                {
                    CarregarPrimeiroComboBox(result.Tables["referencias"]);
                }

                if (result.Tables.Contains("ref_empresas"))
                {
                    CarregarRelacoes(result.Tables["ref_empresas"]);
                }
                CarregarTerceiroComboBox();
            }
            catch (Exception ex)
            {
                MessageBox.Show("Erro ao ler o arquivo com ExcelReaderFactory: " + ex.Message);
            }
        }
        private void CarregarPrimeiroComboBox(DataTable tabelaReferencias)
        {
            if (this.Controls["comboBox1"] is not ComboBox comboBox1 || tabelaReferencias == null) return;

            // Criamos uma tabela auxiliar com colunas para o ID e o valor de exibição
            DataTable comboBoxTable = new();
            comboBoxTable.Columns.Add("ID", typeof(string));
            comboBoxTable.Columns.Add("ValorReferencia", typeof(string));

            // Ignora a primeira linha (cabeçalho)
            bool firstRow = true;
            foreach (DataRow row in tabelaReferencias.Rows)
            {
                if (firstRow)
                {
                    firstRow = false;
                    continue;
                }

                string id = row[0].ToString() ?? string.Empty;
                string valorReferencia = row[1].ToString() ?? string.Empty;

                // Adiciona o ID e o valor ao DataTable auxiliar
                comboBoxTable.Rows.Add(id, valorReferencia);

                // Adiciona a chave no dicionário para o valor selecionado
                if (!empresaRelacionada.ContainsKey(id))
                {
                    empresaRelacionada[id] = new List<string>();
                }

                // Configura o DataTable como fonte de dados para o comboBox1
                comboBox1.DataSource = comboBoxTable;
                comboBox1.DisplayMember = "ValorReferencia";
                comboBox1.ValueMember = "ID";
            }
            comboBox1.SelectedItem = null;
        }
        private void CarregarRelacoes(DataTable tabelaEmpresas)
        {
            // Ignora a primeira linha (cabeçalho)
            bool firstRow = true;
            foreach (DataRow row in tabelaEmpresas.Rows)
            {
                if (firstRow)
                {
                    firstRow = false;
                    continue;
                }

                string idReferencia = row[2].ToString() ?? string.Empty;  // ID da referência relacionada (3ª coluna)
                string valorEmpresa = row[1].ToString() ?? string.Empty;  // Nome da empresa (2ª coluna)

                // Adiciona empresas relacionadas à referência no dicionário
                if (empresaRelacionada.ContainsKey(idReferencia))
                {
                    empresaRelacionada[idReferencia].Add(valorEmpresa);
                }
            }
        }
        private void ComboBox1_SelectedIndexChanged(object? sender, EventArgs e)
        {
            if (sender is not ComboBox comboBox1 || this.Controls["comboBox2"] is not ComboBox comboBox2 || comboBox1.SelectedItem == null) return;

            // Limpa o segundo combobox
            comboBox2.Items.Clear();

            // Obter o ID da referência selecionada (usando ValueMember)
            string idReferenciaSelecionada = comboBox1.SelectedValue?.ToString();            

            // Carrega valores relacionados à seleção do primeiro combobox
            if (idReferenciaSelecionada != null && empresaRelacionada.ContainsKey(idReferenciaSelecionada))
            {
                comboBox2.Items.AddRange(empresaRelacionada[idReferenciaSelecionada].ToArray());
            }
        }
        private void CarregarTerceiroComboBox()
        {
            if (this.Controls["comboBox3"] is not ComboBox comboBox3) return;

            comboBox3.Items.Clear();
            comboBox3.Items.Add("Crédito");
            comboBox3.Items.Add("Débito");

            comboBox3.SelectedIndexChanged += ComboBox3_SelectedIndexChanged;
        }
        private void ComboBox3_SelectedIndexChanged(object? sender, EventArgs e)
        {
            bool isItemSelected = sender is ComboBox comboBox3 && comboBox3.SelectedIndex != null;

            if (this.Controls["textBox1"] is TextBox textBox1) textBox1.Enabled = isItemSelected;
            if (this.Controls["textBox2"] is TextBox textBox2) textBox2.Enabled = isItemSelected;
        }
        private async void IniciarApiPgtoButton_Click(object? sender, EventArgs e){
            try
            {
                if(!runApiPgtoControl)
                {
                    string pythonScriptPath = @"C:\Users\heit_\Documents\USCS\TCC\server_pgto\Code\api_pagamento.py";
                    string venvPythonPath = @"C:\Users\heit_\Documents\USCS\TCC\server_pgto\Scripts\python.exe";

                    ProcessStartInfo startInfo = new()
                    {
                        FileName = venvPythonPath,
                        Arguments = pythonScriptPath,
                        UseShellExecute = false,
                        CreateNoWindow = false
                    };
                    pgtoProcess = new Process {StartInfo = startInfo};
                    await TestarConexao();
                    pgtoProcess.Start();

                    bool apiPgtoOn = await CheckApiOn("http://localhost:5002/health");

                    if (apiPgtoOn)
                    {
                        AdicionaLog("API pagamento inicializada com sucesso");
                        buttonApiPgto.BackColor = System.Drawing.Color.Red;
                        buttonApiPgto.Text = "Desligar API Pgto";
                        runApiPgtoControl = true;
                        EnviarComandoAPI("start_sys");
                    }
                    else
                    {
                        AdicionaLog("TIMEOUT: API pagamento não inicializada após 5 tentativas");
                    }

                }
                else
                {
                    if (pgtoProcess != null && !pgtoProcess.HasExited)
                    {
                        pgtoProcess.Kill();
                        pgtoProcess.WaitForExit(); // Aguarda o processo encerrar
                        buttonApiPgto.BackColor = System.Drawing.Color.Green;
                        buttonApiPgto.Text = "Ligar API Pgto";
                        AdicionaLog("API pagamento encerrada com sucesso");
                    }
                    else
                    {
                        MessageBox.Show("A API não está em execução.", "API PGTO", MessageBoxButtons.OK, MessageBoxIcon.Exclamation);
                        AdicionaLog("ERROR EXEC: A API pagamento não está em execução.");
                    }
                    this.BackColor = System.Drawing.Color.Gray;
                    runApiPgtoControl = false;
                }
                EnableChangeButtonCtr();
            }
            catch (Exception ex)
            {
                MessageBox.Show($@"Error: {ex.Message}", "START ERROR", MessageBoxButtons.OK, MessageBoxIcon.Error);
                AdicionaLog($"ERROR API: A API pagamento não respondeu adequadamente, {ex}");
            }
        }
        private async void IniciarApiBankButton_Click(object? sender, EventArgs e)
        {
            try
            {
                if(!runApiBankControl)
                {
                    string pythonScriptPath = @"C:\Users\heit_\Documents\USCS\TCC\server_pgto\Code\api_financeiro.py";
                    string venvPythonPath = @"C:\Users\heit_\Documents\USCS\TCC\server_pgto\Scripts\python.exe";

                    ProcessStartInfo startInfo = new()
                    {
                        FileName = venvPythonPath,
                        Arguments = pythonScriptPath,
                        UseShellExecute = false,
                        CreateNoWindow = false
                    };
                    bankProcess = new Process {StartInfo = startInfo};
                    bankProcess.Start();

                    bool apiBankOn = await CheckApiOn("http://localhost:5001/health");

                    if(apiBankOn)
                    {
                        AdicionaLog("API bancária inicializada com sucesso");
                        buttonApiBank.BackColor = System.Drawing.Color.Red;
                        buttonApiBank.Text = "Desligar API Bank";
                        runApiBankControl = true;
                    }
                    else
                    {
                        AdicionaLog("TIMEOUT: API bancária não inicializada após 5 tentativas");
                    }

                }
                else
                {
                    if (bankProcess != null && !bankProcess.HasExited)
                    {
                        bankProcess.Kill();
                        bankProcess.WaitForExit(); // Aguarda o processo encerrar
                        buttonApiBank.BackColor = System.Drawing.Color.Green;
                        buttonApiBank.Text = "Ligar API Bank";
                        AdicionaLog("API bancária encerrada com sucesso!");
                    }
                    else
                    {
                        AdicionaLog("ERRO EXEC: A API bancária não está em execução, comando de encerramento inválido");
                    }
                    this.BackColor = System.Drawing.Color.Gray;
                    runApiBankControl = false;
                }
                EnableChangeButtonCtr();
            }
            catch (Exception ex)
            {
                MessageBox.Show($@"Error: {ex.Message}", "START ERROR", MessageBoxButtons.OK, MessageBoxIcon.Error);
                AdicionaLog($"ERROR API: A API bancária não respondeu adequadamente, {ex}");
            }
        }
        private void EnableChangeButtonCtr(){
            pgtoErpEnable = true;
            if(runApiBankControl && runApiPgtoControl)
            {
                buttonCtr.Enabled = true;
                buttonCtr.BackColor = System.Drawing.Color.Green;
                buttonCtr.Text = "ENTRADA ATUAL PGTO->ERP | Click->Maq";
            }
            else
            {
                buttonCtr.Enabled = false;
                buttonCtr.BackColor = System.Drawing.Color.Gray;
                buttonCtr.Text = "Status System: OFF";
            }
        }
        private void ButtonCtr_Click(object? sender, EventArgs e){
            if(ValidateErpMaqChange() && pgtoErpEnable)
            {
                buttonCtr.BackColor = System.Drawing.Color.Blue;
                buttonCtr.Text = "ENTRADA ATUAL PGTO->Maq | Click->ERP";
                pgtoErpEnable = false;
            }
            else
            {
                EnableChangeButtonCtr();
            }

        }
        private void ButtonFaturar_Click(object? sender, EventArgs e)
        {
            List<string> campos = new();
            Dictionary<string, string> dados = new();

            ComboBox comboBox1 = (ComboBox)this.Controls["comboBox1"];
            string valorRamo = comboBox1.SelectedItem?.ToString() ?? "NaN";
            if(valorRamo == "NaN") campos.Add("Ramo");
            else dados.Add("Ramo", valorRamo);

            ComboBox comboBox2 = (ComboBox)this.Controls["comboBox2"];
            string valorEmpresa = comboBox2.SelectedItem?.ToString() ?? "NaN";
            if(valorEmpresa == "NaN") campos.Add("Empresa");
            else dados.Add("Empresa", valorEmpresa);

            ComboBox comboBox3 = (ComboBox)this.Controls["comboBox3"];
            string valorFormaPgto = comboBox3.SelectedItem?.ToString() ?? "NaN";
            if(valorFormaPgto == "NaN") campos.Add("Forma de Pagamento");
            else dados.Add("tp_pgto", valorFormaPgto);

            TextBox textBox1 = (TextBox)this.Controls["textBox1"];
            string valorParcelas = textBox1.Text;
            if(valorParcelas == "NaN" && valorFormaPgto == "Crédito") campos.Add("Parcelas");
            else if (valorFormaPgto == "Crédito") dados.Add("Parcelas", valorParcelas);

            TextBox textBox2 = (TextBox)this.Controls["textBox2"];
            string valorTotalPgto = textBox2.Text;
            if(valorTotalPgto == "NaN") campos.Add("Valor");
            else dados.Add("Valor", valorTotalPgto);

            if (campos.Count > 0)
            {
                string itens = string.Join("\n-", campos);
                string mensagem = $"Não é possível faturar sem informar os seguintes campos:\n-{itens}";
                AlertBoxMessageOn(mensagem, "ERRO INFORMAÇÕES");
            }
            else
            {
                EnviarComandoAPI("fatura_maq",dados);
            }
        }
        private static void AlertBoxMessageOn(string message, string caption)
        {
            MessageBox.Show(message, caption, MessageBoxButtons.OK, MessageBoxIcon.Error);
        }
        private bool ValidateErpMaqChange()
        {
            if ((this.Controls["comboBox1"] is not ComboBox comboBox1) || (this.Controls["comboBox2"] is not ComboBox comboBox2)) return false;
            if ((comboBox1.SelectedItem == null) || (comboBox2.SelectedItem == null)) return false;
            else return true;
        }
        private void AdicionaLog(string mensagem)
        {
            if(outputTextBox.InvokeRequired)
            {
                outputTextBox.Invoke(new Action(() => AdicionaLog(mensagem)));
            }
            else
            {  
                outputTextBox.AppendText($"{DateTime.Now}: {mensagem}\r\n");
                outputTextBox.SelectionStart = outputTextBox.Text.Length;
                outputTextBox.ScrollToCaret();
            }
        }
        private void SetupForm()
        {
            this.Text = "Minha Interface";
            this.Size = new System.Drawing.Size(400, 600);
            this.BackColor = System.Drawing.Color.Gray;

            List<string> labelTexts = new() { "Ramo:", "Empresa:", "Forma de Pagamento:", "Parcelas:", "Valor:" };
            List<string> buttonTexts = new() { "Cadastro", "Faturar", "Cancelar", "Sair" };
            
            //Botão para controle de pagamento remoto ou local
            buttonApiPgto = new()
            {
                Text = "Ligar API Pgto",
                Location = new System.Drawing.Point(15, 10),
                Width = 150,
                Height = 30,
                Font = new System.Drawing.Font("Arial", 10, System.Drawing.FontStyle.Bold),
                BackColor = System.Drawing.Color.Green,
                ForeColor = System.Drawing.Color.White,
            };
            buttonApiPgto.Click += IniciarApiPgtoButton_Click;
            this.Controls.Add(buttonApiPgto);

            buttonApiBank = new()
            {
                Text = "Ligar API Bank",
                Location = new System.Drawing.Point(215, 10),
                Width = 150,
                Height = 30,
                Font = new System.Drawing.Font("Arial", 10, System.Drawing.FontStyle.Bold),
                BackColor = System.Drawing.Color.Green,
                ForeColor = System.Drawing.Color.White,
            };
            buttonApiBank.Click += IniciarApiBankButton_Click;
            this.Controls.Add(buttonApiBank);

            buttonCtr = new()
            {
                Text = "Status System: OFF",
                Location = new System.Drawing.Point(40, 50),
                Width = 300,
                Height = 30,
                Font = new System.Drawing.Font("Arial", 10, System.Drawing.FontStyle.Bold),
                BackColor = System.Drawing.Color.Gray,
                ForeColor = System.Drawing.Color.White,
                Enabled = false
            };
            buttonCtr.Click += ButtonCtr_Click;
            this.Controls.Add(buttonCtr);

            //Insere os Labels e seus ComboBox's
            for (int i = 0; i < 3; i++)
            {
                Label label = new()
                {
                    Text = labelTexts[i],
                    Location = new System.Drawing.Point(10, 100 + i * 30),
                    Width = 150
                };
                this.Controls.Add(label);

                ComboBox comboBox = new()
                {
                    Location = new System.Drawing.Point(180, 100 + i * 30),
                    Name = $"comboBox{i + 1}"
                };
                this.Controls.Add(comboBox);

                // Associa o evento SelectedIndexChanged ao primeiro combobox
                if (i == 0)
                {
                    comboBox.SelectedIndexChanged += ComboBox1_SelectedIndexChanged;
                }
            }

            //Insere os Labels e seus TextInput's
            for (int i = 0; i < 2; i++)
            {
                Label label = new()
                {
                    Text = labelTexts[3 + i],
                    Location = new System.Drawing.Point(10, 190 + i * 30)
                };
                this.Controls.Add(label);

                TextBox textBox = new()
                {
                    Location = new System.Drawing.Point(180, 190 + i * 30),
                    Width = 150,
                    Name = $"textBox{i + 1}",
                    Enabled = false
                };
                this.Controls.Add(textBox);
            }

            //Insere os botões
            int btn =0;
            Button buttonCadastro = new()
            {
                Text = buttonTexts[btn],
                Location = new System.Drawing.Point(10 + btn * 90, 260),
                Width = 80
            };
            this.Controls.Add(buttonCadastro);
            btn++;
            Button buttonFaturar = new()
            {
                Text = buttonTexts[btn],
                Location = new System.Drawing.Point(10 + btn * 90, 260),
                Width = 80,
            };
            buttonFaturar.Click += ButtonFaturar_Click;
            this.Controls.Add(buttonFaturar);
            btn++;
            Button buttonCancelar = new()
            {
                Text = buttonTexts[btn],
                Location = new System.Drawing.Point(10 + btn * 90, 260),
                Width = 80
            };
            this.Controls.Add(buttonCancelar);
            btn++;
            Button buttonSair = new()
            {
                Text = buttonTexts[btn],
                Location = new System.Drawing.Point(10 + btn * 90, 260),
                Width = 80
            };
            this.Controls.Add(buttonSair);

            //Insere o campo de log
            Label outputLabel = new()
            {
                Text = "Output Log:",
                Location = new System.Drawing.Point(10, 300)
            };
            this.Controls.Add(outputLabel);

            outputTextBox = new()
            {
                Location = new System.Drawing.Point(10, 325),
                Width = 360,
                Height = 220,
                Multiline = true,
                ReadOnly = true,
                ScrollBars = ScrollBars.Vertical
            };
            this.Controls.Add(outputTextBox);
        }
        private async Task<bool> CheckApiOn(string url, int tentativas = 5, int intervaloMs = 1000)
        {
            for(int i = 0; i < tentativas; i++)
            {
                try
                {
                    var response = await client.GetAsync(url);
                    if (response.IsSuccessStatusCode)
                    {
                        return true;
                    }
                }
                catch(Exception)
                {
                    AdicionaLog($"{url} - tentativa {i+1}");
                }
                await Task.Delay(intervaloMs);
            }
            return false;
        }
        public async Task IniciarSignalR(int port)
        {
            string protocol = port == 7246 ? "https" : "http";
            string url = $"{protocol}://localhost:{port}/signalrhub";
            var connection = new HubConnectionBuilder()
                .WithUrl(url, options => 
                { 
                    options.HttpMessageHandlerFactory = _ => new HttpClientHandler
                    {
                        ServerCertificateCustomValidationCallback = HttpClientHandler.DangerousAcceptAnyServerCertificateValidator 
                    };
                })
                .Build();

            try
            {
                await connection.StartAsync();
                AdicionaLog($"SignalR: Conexão SignalR estabelecida com sucesso");
            }
            catch (Exception ex)
            {
                AdicionaLog($"Erro ao iniciar conexão SignalR: {ex.Message}");
                return;
            }
            connection.On<string>("SendMessage", (status) =>
            {
                AdicionaLog($"API(ws) STATUS: {status}");
            });
        }
        private async void EnviarComandoAPI(string comando, Dictionary<string,string>? dados = null){
            string url = $"http://localhost:5002/{comando}";
            var json = JsonSerializer.Serialize(dados);
            var content = new StringContent(json, Encoding.UTF8, "application/json");

            try
            {
                var response = await client.PostAsync(url, content);
                if (response.IsSuccessStatusCode)
                {
                    var responseContent = await response.Content.ReadAsStringAsync();
                    var responseData = JsonSerializer.Deserialize<Dictionary<string, JsonElement>>(responseContent);
                    if(responseData != null && responseData.TryGetValue("resp", out JsonElement respElement))
                    {
                        string? respValue= respElement.GetString();
                        AdicionaLog($"API - {comando}: {response.StatusCode} - {respValue}");
                    }
                }
                else
                {
                    AdicionaLog($"Erro na requisição {comando}: {response.StatusCode}");
                }
            }
            catch (Exception ex)
            {
                AdicionaLog($"ERRO de comunicação com API_PGTO: {ex}");
            }
        }
        private void StopAspNetServer(object sender, FormClosingEventArgs e) { 
            if (aspnetProcess != null && !aspnetProcess.HasExited) { 
                aspnetProcess.Kill();
                aspnetProcess.Dispose(); 
            } 
        }
    }
}
