# santos-maritime-intelligence-LLM

## Visão Geral
Este projeto implementa um sistema avançado de monitoramento marítimo focado no Porto de Santos, o maior complexo portuário da América Latina. A solução combina modelos de detecção de objetos em tempo real com a capacidade analítica de Large Language Models (LLMs) para identificar, classificar e gerar relatórios contextuais sobre o tráfego de embarcações.

O diferencial deste repositório é a camada de inteligência multimodal, que não apenas detecta o barco, mas utiliza LLMs para interpretar a cena, identificar comportamentos anômalos ou descrever características técnicas da embarcação via prompts.

## Funcionalidades
Detecção de Precisão: Identificação de navios cargueiros, petroleiros, rebocadores e barcos de lazer.

Análise via LLM: Integração com modelos multimodais para descrição de incidentes ou status do convés.

Dashboard de Telemetria: Visualização de dados de tráfego em tempo real.

## Stack Tecnológica
Linguagem: Python

Visão Computacional: YOLO

LLMs/VLM: Integração com GPT-4o, Claude 3.5 Sonnet ou modelos locais (Llava / BakLLaVA) via Ollama/vLLM (ainda nao foi decidido e sera feito apenas quando a etapa for alcançada).

Processamento de Dados: OpenCV, Pandas e NumPy.

Orquestração: Docker para o ambiente de execução (outros metodos podem ser utilizados de acordo com a necessidade do projeto).
