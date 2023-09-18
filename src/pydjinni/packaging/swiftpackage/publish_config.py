from pydantic import BaseModel, HttpUrl, Field


class SwiftpackagePublishConfig(BaseModel):
    repository: HttpUrl = Field(
        description="Http Url to git repository",
        examples=[
            "https://github.com/foo/bar.git"
        ]
    )
    branch: str = Field(
        default="main",
        description="Git repository branch that the package should be pushed to."
    )
    username: str = Field(
        default=None,
        description="Username of git repository"
    )
    password: str = Field(
        default=None,
        description="Password (token) to access the git repository."
                    "It is recommended to set this via the environment variable "
                    "`PACKAGE__SWIFTPACKAGE__PUBLISH__PASSWORD`"
    )
