from pydantic import BaseModel, HttpUrl, Field


class AndroidArchivePublishConfig(BaseModel):
    """
    Maven publishing information
    """
    maven_registry: HttpUrl = Field(
        default=None,
        description="Url of the maven registry that the package should be published to."
    )
    group_id: str = Field(
        description="Maven package groupId"
    )
    artifact_id: str = Field(
        description="Maven package artifactId"
    )
    username: str = Field(
        default=None,
        description="Username for the maven registry"
    )
    password: str = Field(
        default=None,
        description="Password (token) to access the maven registry."
                    "It is recommended to set this via the environment variable "
                    "`PACKAGE__AAR__PUBLISH__PASSWORD`"
    )
