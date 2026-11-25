# HACKATHON Bovinu's
# 🍽️ EcoPrato — Reconhecimento de Alimentos e Controle de Peso por Visão Computacional

> **EcoPrato** é uma aplicação web desenvolvida em **FastAPI** e **SQLite** com frontend em **HTML/JS** e captura ao vivo por **webcam**. Utiliza a **API do Gemini** para identificar alimentos em fotos de pratos de restaurante por quilo, estimar e calibrar o peso em gramas (com integração opcional de balança), registrar o consumo por cliente e gerar relatórios diários consolidados em `g` e `kg` no fuso horário `America/Sao_Paulo`.

---

## ✨ Funcionalidades

- **Análise multimodal de pratos:** identifica múltiplos alimentos em uma mesma foto e retorna o peso estimado e o nível de confiança de cada item.
- **Calibração proporcional com balança:** se o peso total da balança (`peso_balanca_gramas`) for informado, os pesos individuais estimados pela IA são ajustados proporcionalmente para bater exatamente com a pesagem real.
- **Normalização de nomes:** agrupa sinônimos comuns (ex.: *arroz* → *arroz branco*, *frango* → *frango grelhado*) para manter os relatórios consistentes.
- **Captura ao vivo pela webcam ou upload:** tire fotos direto da câmera no navegador (com opção de envio automático) ou envie arquivos `JPEG`, `PNG` e `WEBP`.
- **Fluxo rápido de atendimento:** opções para limpar o peso da balança e incrementar automaticamente o ID do cliente/comanda (`cli_001` → `cli_002`) após cada registro.
- **Relatório diário por alimento:** consulta agregada por data no fuso `America/Sao_Paulo`, exibindo total em gramas, quilogramas e quantidade de porções servidas.

---

## 🛠️ Tecnologias Utilizadas

| Camada | Tecnologia |
| :--- | :--- |
| **Backend** | Python 3.10+, FastAPI, Uvicorn, Pydantic |
| **IA / Visão** | Google GenAI SDK (`gemini-2.5-flash`) com Structured Outputs |
| **Banco de Dados** | SQLite (`sqlite3`) |
| **Frontend** | HTML5, CSS3, JavaScript (Fetch API + MediaDevices / Webcam) |

---

## 🖥️ Solução (em imagens)
<img width="1832" height="705" alt="image" src="https://github.com/user-attachments/assets/d418b24f-dd29-418a-a274-a001520d1710" />

---

## 🎞️ Vídeo de Apresentação

---

## 🎓 Slides

---

## 📁 Estrutura do Projeto

```text
kilo-ia/
├── app/
│   ├── __init__.py
│   ├── main.py              # Rotas da API e entrega do frontend
│   ├── schemas.py           # Modelos Pydantic de entrada e saída
│   ├── vision.py            # Integração com Gemini e cálculo proporcional de pesos
│   ├── database.py          # Inicialização e consultas no SQLite
│   ├── static/              # Arquivos estáticos (ex.: logo.jpg)
│   └── templates/
│       └── index.html         # Interface web com webcam e relatório diário
├── data/                    # Banco SQLite gerado localmente (ignorado no Git)
├── .env.example             # Exemplo de variáveis de ambiente
├── .gitignore
└── requirements.txt
'''


