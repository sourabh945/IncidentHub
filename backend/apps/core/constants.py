from typing import ClassVar

class Role:
    OWNER = "owner"
    ADMIN = "admin"
    MANAGER = "manager"
    TEAM_LEAD = "team_lead"
    DEVELOPER = "developer"


    CHOICES: ClassVar[list[tuple[str, str]]] = [
        (OWNER, "Owner"),
        (ADMIN, "Admin"),
        (MANAGER, "Manager"),
        (TEAM_LEAD, "Team Lead"),
        (DEVELOPER, "Developer"),
    ]

    ALL: ClassVar[tuple[str, ...]] = (OWNER, ADMIN, MANAGER, TEAM_LEAD, DEVELOPER)

    RANK: ClassVar[dict[str, int]] = {
        OWNER: 5,
        ADMIN: 4,
        MANAGER: 3,
        TEAM_LEAD: 2,
        DEVELOPER: 1,
    }

    @classmethod
    def at_least(cls, role, minimum):
        return cls.RANK[role] >= cls.RANK[minimum]
