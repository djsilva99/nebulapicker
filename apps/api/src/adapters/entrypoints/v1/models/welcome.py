from pydantic import BaseModel

WELCOME_MESSAGE=(
    "<p>NebulaPicker is a powerful, self-hosted content curation API designed "
    "for teams and individuals who want complete control over how they "
    "discover and consume information. It automatically aggregates content "
    "from multiple RSS feeds and transforms raw, high-volume data into a "
    "focused, high-signal stream tailored to your exact interests.</p>"
    "<p>Using flexible, user-defined filtering rules, NebulaPicker removes "
    "noise such as duplicate entries, low-value posts, and irrelevant topics "
    "before they ever reach you. The result is a clean, structured feed that "
    "surfaces only the most relevant content — ready to be consumed by "
    "applications, dashboards, newsletters, or downstream automation "
    "tools.</p>"
    "<p> Built with performance, extensibility, and data ownership in mind, "
    "NebulaPicker fits seamlessly into modern workflows. Whether you’re "
    "powering a custom news reader, monitoring industry trends, fueling "
    "research pipelines, or building curated content experiences for users, "
    "NebulaPicker provides a reliable foundation for scalable content "
    "intelligence.</p>"
)

class WelcomeResponse(BaseModel):
    message: str = WELCOME_MESSAGE
