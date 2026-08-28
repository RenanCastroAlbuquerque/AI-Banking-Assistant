import os
from agents import Agent, Runner, function_tool

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("A variável OPENAI_API_KEY não foi configurada.")

os.environ["OPENAI_API_KEY"] = api_key

saldo = 500.00

@function_tool
def realizar_pix (chave_pix: str, valor: float) -> str:
  global saldo

  if valor <= 0:
    return "O valor do PIX deve ser maior que 0"

  if saldo < valor:
    return f"Saldo insuficiente. Saldo disponivel R$ {saldo:.2f}"

  saldo -= valor
  return (
      f"PIX de R$ {valor:.2f} realizado para {chave_pix} com sucesso."
      f"Saldo disponivel: R$ {saldo:.2f}"
  )

@function_tool
def consultar_saldo() -> str:
  global saldo
  return f"Saldo disponivel: R$ {saldo:.2f}"

agent_duvida = Agent(
    name = "Especilista em duvidas",
    instructions = ("responde perguntas sobre produtos, serviços, tarifas, PIX, cartões e outras informações do banco fictício."),
    model = "gpt-4o-mini",
)

agent_atendimento = Agent(
    name = "Assistente de Atendimento",
    handoff_description = "Use para ser responsável pelo atendimento",
    instructions = "Faça a triagem do cliente e encaminhe a solicitação para o especialista adequado.",
    model = "gpt-4o-mini",
)

agent_pix = Agent(
    name = "Especialista em PIX",
    instructions = (
        "Você é responsável por operações de PIX. "
        "Quando o cliente fornecer uma chave PIX e um valor, "
        "use a ferramenta realizar_pix para executar a operação."
        ),
    tools = [
        realizar_pix,
        consultar_saldo,

        agent_atendimento.as_tool(
            tool_name = "Consultar_atendimento",
            tool_description = "Use para consultar o Assistente atendimento ",
        ),

        agent_duvida.as_tool(
            tool_name = "Consultar_especialista_em_duvidas",
            tool_description = "Use para consultar o especialista em duvidas",
        ),
        ],
    model = "gpt-4o-mini",
)

agent_atendimento.handoffs = [agent_duvida, agent_pix]

historico = []

while True:
    mensagem = input("Você: ")

    if mensagem.lower() == "sair":
        break

    historico.append({
        "role": "user",
        "content": mensagem
    })

    resultado = await Runner.run(
        agent_atendimento,
        historico
    )

    print("Agente:", resultado.final_output)

    historico.append({
        "role": "assistant",
        "content": resultado.final_output
    })