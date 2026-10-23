from db.base_stage_repository import BaseSingleStageRepository
from db.base_stage_services import BaseSingleStageService
from db.models import Message, Portfolio
from sqlalchemy.ext.asyncio import AsyncSession

from services.external.ai.client import AIClient
from services.chat.rag_service import RAGService
from typing import Optional

OFF_TOPIC_REPLY = (
    "I'm only here to answer questions about this person's professional background — "
    "things like their skills, work experience, education, and projects. "
    "Feel free to ask me anything along those lines!"
)


def build_system_prompt(portfolio: Portfolio, context: str) -> str:
    full_name = f"{portfolio.first_name} {portfolio.last_name}"
    return f"""You are a professional AI representative for {full_name}'s portfolio website.
Visitors come here to learn about {portfolio.first_name}'s professional background.

YOUR ONLY JOB:
Answer questions about {full_name}'s professional life using ONLY the verified portfolio information provided below.

STRICT RULES — you must follow all of these without exception:
1. NEVER answer questions unrelated to {full_name}'s professional background. This includes (but is not limited to): geography, history, science, politics, math, general knowledge, or any topic not directly about this person.
2. NEVER use your general training knowledge to fill gaps. If the answer is not in the portfolio information below, say you don't have that detail and suggest the visitor reach out directly.
3. ALWAYS respond in the same language the visitor used — if they write in Persian, reply in Persian; if English, reply in English. But NEVER let the language change what you talk about.
4. Keep answers concise, warm, and professional — like a knowledgeable colleague speaking on {portfolio.first_name}'s behalf.
5. Refer to {portfolio.first_name} by first name. Never say "the candidate" or "the user".
6. If a question is off-topic, decline politely in the visitor's language and redirect them to ask about {portfolio.first_name}'s background.

ABOUT {full_name.upper()}:
Title: {portfolio.title}
Summary: {portfolio.summary}

VERIFIED PORTFOLIO DETAILS:
{context}

Remember: You represent {portfolio.first_name} professionally. Every response reflects on their personal brand."""


class MessageService(BaseSingleStageService[Message]):
    def __init__(self, message_repo: BaseSingleStageRepository = None):
        self.message_repo = message_repo or BaseSingleStageRepository(Message)
        super().__init__(self.message_repo, Message)


class AIChatService:
    def __init__(
        self,
        ai_client: AIClient,
        message_service: MessageService,
        rag_service: Optional[RAGService] = None,
    ):
        self.ai_client = ai_client
        self.message_service = message_service
        self.rag_service = rag_service

    async def chat(
        self,
        session: AsyncSession,
        session_id,
        user_message: str,
        portfolio: Portfolio,
    ) -> str:
        await self.message_service.repo.create(
            session=session,
            session_id=session_id,
            role="user",
            portfolio_id=portfolio.id,
            content=user_message,
        )

        retrieved_context: str | None = None
        if self.rag_service:
            try:
                retrieved_context = await self.rag_service.retrieve_context(
                    portfolio_id=portfolio.id,
                    query=user_message,
                    top_k=3,
                )
            except Exception as e:
                print(f"[RAG] retrieval error: {e}")

        if retrieved_context is None:
            await self.message_service.create(
                session=session,
                session_id=session_id,
                role="assistant",
                portfolio_id=portfolio.id,
                content=OFF_TOPIC_REPLY,
            )
            # return OFF_TOPIC_REPLY
            return self.ready_response(portfolio, user_message)

        system_prompt = build_system_prompt(portfolio, retrieved_context)

        history, _ = await self.message_service.find(
            session=session,
            filters={
                "session_id": {"match_mode": "equals", "value": session_id},
                "portfolio_id": {"match_mode": "equals", "value": portfolio.id},
            },
            limit=10,
        )

        messages = [{"role": "system", "content": system_prompt}]
        messages += [{"role": msg.role, "content": msg.content} for msg in history]

        ai_response = await self.ai_client.chat(messages)

        # Persist assistant reply
        await self.message_service.create(
            session=session,
            session_id=session_id,
            role="assistant",
            portfolio_id=portfolio.id,
            content=ai_response,
        )
        return ai_response

    def ready_response(self, portfolio: Portfolio, question: str) -> str:
        readies = {
            "What is your tech stack?": f"{portfolio.first_name} is a {portfolio.title} and proficient in {", ".join([skill for skill in portfolio.profile_data.get('skills', []) if skill][:5])}.",
            "Where have you worked?": f"{portfolio.first_name} has worked at {", ".join([job["company"] for job in portfolio.profile_data.get('experiences', []) if job])}.",
        }
        return readies.get(question, OFF_TOPIC_REPLY)