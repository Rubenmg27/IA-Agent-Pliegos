from strands.hooks import AgentInitializedEvent, HookProvider, HookRegistry, MessageAddedEvent
from bedrock_agentcore_starter_toolkit.operations.memory.manager import MemoryManager
from bedrock_agentcore.memory.constants import ConversationalMessage, MessageRole
from bedrock_agentcore.memory.session import MemorySession, MemorySessionManager
import logging

# Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("personal-agent")

class Memory:
    """
    Hook to manage conversational memory using Bedrock Agent Core.
    """

    def __init__(self, actor_id: str, session_id: str, region:str, name_memory:str):
        self.region = region
        self.actor_id = actor_id
        self.session_id = session_id
        self.name_memory = name_memory
        self.memory_manager = MemoryManager(region_name=self.region)

        try:
            self.memory = self.memory_manager.get_or_create_memory(
                name=self.name_memory,
                strategies=[],
                event_expiry_days=7,
                memory_execution_role_arn=None,
            )
            self.memory_id = self.memory.id
        except Exception as e:
            import traceback
            traceback.print_exc()
            if 'memory_id' in locals():
                self.memory_manager.delete_memory(self.memory_id)
            raise e

    def initialize_session(self):
        self.session_manager = MemorySessionManager(memory_id=self.memory.id, region_name=self.region)
        self.user_session = self.session_manager.create_memory_session(
            actor_id = self.actor_id,
            session_id=self.session_id
        )
        return self.user_session

class MemoryHookProvider(HookProvider):
    def __init__(self, memory_session: MemorySession):  # Accept MemorySession instead
        self.memory_session = memory_session

    def on_agent_initialized(self, event: AgentInitializedEvent):
        """Load recent conversation history when agent starts using MemorySession"""
        try:
            # Use the pre-configured memory session (no need for actor_id/session_id)
            recent_turns = self.memory_session.get_last_k_turns(k=5)

            if recent_turns:
                # Format conversation history for context
                context_messages = []
                for turn in recent_turns:
                    for message in turn:
                        # Handle both EventMessage objects and dict formats
                        if hasattr(message, 'role') and hasattr(message, 'content'):
                            role = message['role']
                            content = message['content']
                        else:
                            role = message.get('role', 'unknown')
                            content = message.get('content', {}).get('text', '')
                        context_messages.append(f"{role}: {content}")

                context = "\n".join(context_messages)
                # Add context to agent's system prompt
                event.agent.system_prompt += f"\n\nRecent conversation:\n{context}"
                logger.info(f"✅ Loaded {len(recent_turns)} conversation turns using MemorySession")

        except Exception as e:
            logger.error(f"Memory load error: {e}")

    def on_message_added(self, event: MessageAddedEvent):
        """Store messages in memory using MemorySession"""
        messages = event.agent.messages
        try:
            if messages and len(messages) > 0 and messages[-1]["content"][0].get("text"):
                message_text = messages[-1]["content"][0]["text"]
                message_role = MessageRole.USER if messages[-1]["role"] == "user" else MessageRole.ASSISTANT

                # Use memory session instance (no need to pass actor_id/session_id)
                result = self.memory_session.add_turns(
                    messages=[ConversationalMessage(message_text, message_role)]
                )

                event_id = result['eventId']
                logger.info(f"✅ Stored message with Event ID: {event_id}, Role: {message_role.value}")

        except Exception as e:
            logger.error(f"Memory save error: {e}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")

    def register_hooks(self, registry: HookRegistry):
        # Register memory hooks
        registry.add_callback(MessageAddedEvent, self.on_message_added)
        registry.add_callback(AgentInitializedEvent, self.on_agent_initialized)
        logger.info("✅ Memory hooks registered with MemorySession")


