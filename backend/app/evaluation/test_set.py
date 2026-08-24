TEST_SET = [
    # =========================
    # REORDERED FOR TOP_K=10 RETEST — weak recall questions + controls first
    # (original full list preserved below, nothing deleted)
    # =========================

    {
        "question": "What is an LLM agent?",
        "reference": "An LLM agent is a system that uses a large language model to reason about tasks, decide what actions to take, and interact with tools or external environments to accomplish a goal.",
    },
    {
        "question": "What is the role of memory in an LLM agent?",
        "reference": "Memory allows an LLM agent to retain and use relevant information from previous interactions or intermediate steps, helping it make better decisions over the course of a task.",
    },
    {
        "question": "How do tools and observations interact in an LLM agent?",
        "reference": "The agent selects and executes a tool, receives the tool's output as an observation, and can then use that observation to determine its next action or generate a final response.",
    },
    {
        "question": "Why is fine-tuning useful for large language models?",
        "reference": "Fine-tuning allows a pretrained language model to specialize in particular tasks, domains, or behaviors without training a model entirely from scratch.",
    },
    {
        "question": "What challenges can occur when fine-tuning large language models?",
        "reference": "Fine-tuning can require significant computational resources and suitable training data, and it can cause issues such as overfitting or loss of previously learned capabilities.",
    },
    {
        "question": "What is retrieval augmented generation?",
        "reference": "RAG is a technique that enhances generative language models by retrieving relevant external documents or knowledge during generation instead of relying only on knowledge stored in the model parameters.",
    },
    {
        "question": "How do LLM agents use tools?",
        "reference": "LLM agents use tools to execute actions that the language model cannot reliably perform by itself, such as calculations, searching information, or interacting with external systems.",
    },
    {
        "question": "How are cognitive architectures related to language agents?",
        "reference": "Cognitive architectures provide structured mechanisms for memory, reasoning, decision making, and actions that can be applied to LLM-based language agents to give them more systematic behavior.",
    },

    # =========================
    # Remaining original questions (unchanged, kept for the full run later)
    # =========================

    {
        "question": "Why is retrieval useful for large language models?",
        "reference": "Retrieval provides language models with relevant external information at inference time, which can improve factuality and allow them to use knowledge that may not be stored in their parameters.",
    },
    {
        "question": "How does RAG combine retrieval and generation?",
        "reference": "RAG first retrieves relevant information from an external knowledge source and then provides that information as context to a generative language model to produce the answer.",
    },
    {
        "question": "What are some limitations or challenges of retrieval augmented generation?",
        "reference": "RAG systems can suffer from poor retrieval quality, irrelevant or incomplete context, and difficulty generating reliable answers when the retrieved information is insufficient.",
    },
    {
        "question": "How can retrieval augmented generation improve the factuality of language model responses?",
        "reference": "RAG can improve factuality by grounding the language model's response in relevant retrieved documents instead of requiring the model to rely entirely on its parametric knowledge.",
    },
    {
        "question": "Why might an LLM agent need a calculator tool?",
        "reference": "A calculator tool allows an LLM agent to perform mathematical computations accurately instead of relying on the language model to generate the calculation itself.",
    },
    {
        "question": "What is fine-tuning of a large language model?",
        "reference": "Fine-tuning is the process of further training a pretrained language model on a specific dataset or task so that the model adapts its behavior or capabilities to that target domain.",
    },
    {
        "question": "What is the difference between pretraining and fine-tuning?",
        "reference": "Pretraining learns general language representations from large amounts of data, while fine-tuning further adapts the pretrained model using data targeted toward a particular task or domain.",
    },
    {
        "question": "How can fine-tuning adapt a language model to a specific domain?",
        "reference": "A language model can be fine-tuned on domain-specific examples so that its parameters adapt to the terminology, patterns, and tasks associated with that domain.",
    },
    {
        "question": "Who was the first person to walk on Mars?",
        "reference": "The provided paper corpus does not contain information about a person walking on Mars.",
    },
    {
        "question": "What is the capital city of Australia?",
        "reference": "The provided paper corpus does not contain information about the capital city of Australia.",
    },
    {
        "question": "What is the boiling point of water at sea level?",
        "reference": "The provided paper corpus does not contain information about the boiling point of water at sea level.",
    },
]