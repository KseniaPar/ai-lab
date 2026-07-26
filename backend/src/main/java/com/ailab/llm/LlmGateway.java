package com.ailab.llm;

import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.chat.model.ChatModel;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

@Service
public class LlmGateway {

    private final ChatClient chatClient;
    private final boolean configured;

    public LlmGateway(ChatModel chatModel, @Value("${app.openrouter.api-key:}") String apiKey) {
        this.chatClient = ChatClient.builder(chatModel).build();
        this.configured = apiKey != null && !apiKey.isBlank() && !"sk-not-set".equals(apiKey.trim());
    }

    public boolean configured() {
        return configured;
    }

    public String complete(String system, String user) {
        if (!configured) {
            throw new IllegalStateException("OPENROUTER_API_KEY не задан — LLM недоступен");
        }
        return chatClient.prompt()
                .system(system)
                .user(user)
                .call()
                .content();
    }
}
