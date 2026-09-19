from sqlalchemy import Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.database import Base

class UserSession(Base):
    __tablename__ = "tbl_UserSessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    session_id: Mapped[str] = mapped_column(String, unique=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("tbl_Users.id"), index=True, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, index=True, nullable=False)
    expires_at: Mapped[DateTime] = mapped_column(DateTime, index=True, nullable=False)

    user: Mapped["Users"] = relationship()

class Users(Base):
    __tablename__ = "tbl_Users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String, unique=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    phone: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=True)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    active: Mapped[int] = mapped_column(Integer, default=0)

class SteamGames(Base):
    __tablename__ = "tbl_SteamGames"

    appid: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    short_description: Mapped[str] = mapped_column(String, index=False, nullable=True)
    about_the_game: Mapped[str] = mapped_column(String, index=False, nullable=True)
    publisher: Mapped[str] = mapped_column(String, index=True, nullable=True)
    developer: Mapped[str] = mapped_column(String, index=True, nullable=True)
    release_date: Mapped[str] = mapped_column(String, index=True, nullable=True)
    price: Mapped[float] = mapped_column(Float, index=True, nullable=True)
    website: Mapped[str] = mapped_column(String, index=False, nullable=True)
    pc_requirements: Mapped[str] = mapped_column(String, index=False, nullable=True)
    recommendations: Mapped[int] = mapped_column(Integer, index=True, nullable=True)
    metacritic_score: Mapped[float] = mapped_column(Float, index=True, nullable=True)
    header_image_url: Mapped[str] = mapped_column(String, index=False, nullable=False)
    capsule_image_url: Mapped[str] = mapped_column(String, index=False, nullable=True)
    background_image_url: Mapped[str] = mapped_column(String, index=False, nullable=True)

    genres: Mapped[list["Genres"]] = relationship(
        secondary="tbl_SteamGenres"
    )

    languages: Mapped[list["Languages"]] = relationship(
        secondary="tbl_SteamLanguages"
    )

    platforms: Mapped[list["Platforms"]] = relationship(
        secondary="tbl_SteamPlatforms"
    )

    tags: Mapped[list["Tags"]] = relationship(
        secondary="tbl_SteamTags"
    )


class SteamGenres(Base):
    __tablename__ = "tbl_SteamGenres"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    appid: Mapped[int] = mapped_column(Integer, ForeignKey("tbl_SteamGames.appid"), index=True, nullable=False)
    genre_id: Mapped[int] = mapped_column(Integer, ForeignKey("tbl_Genres.id"), index=True, nullable=False)

class Genres(Base):
    __tablename__ = "tbl_Genres"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    genre: Mapped[str] = mapped_column(String, index=True, nullable=False, unique=True)

class SteamLanguages(Base):
    __tablename__ = "tbl_SteamLanguages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    appid: Mapped[int] = mapped_column(Integer, ForeignKey("tbl_SteamGames.appid"), index=True, nullable=False)
    language_id: Mapped[int] = mapped_column(Integer, ForeignKey("tbl_Languages.id"), index=True, nullable=False)

class Languages(Base):
    __tablename__= "tbl_Languages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    language: Mapped[str] = mapped_column(String, index=True, nullable=False, unique=True)

class SteamTags(Base):
    __tablename__ = "tbl_SteamTags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    appid: Mapped[int] = mapped_column(Integer, ForeignKey("tbl_SteamGames.appid"), index=True, nullable=False)
    tag_id: Mapped[int] = mapped_column(Integer, ForeignKey("tbl_Tags.id"), index=True, nullable=False)

class Tags(Base):
    __tablename__= "tbl_Tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    tag: Mapped[str] = mapped_column(String, index=True, nullable=False, unique=True)

class SteamPlatforms(Base):
    __tablename__ = "tbl_SteamPlatforms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    appid: Mapped[int] = mapped_column(Integer, ForeignKey("tbl_SteamGames.appid"), index=True, nullable=False)
    platform_id: Mapped[int] = mapped_column(Integer, ForeignKey("tbl_Platforms.id"), index=True, nullable=False)

class Platforms(Base):
    __tablename__ = "tbl_Platforms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    platform: Mapped[str] = mapped_column(String, index=True, nullable=False, unique=True)

class SteamScreenshots(Base):
    __tablename__ = "tbl_SteamScreenshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    appid: Mapped[int] = mapped_column(Integer, ForeignKey("tbl_SteamGames.appid"), index=True, nullable=False)
    screenshot_url: Mapped[str] = mapped_column(String, index=False, nullable=False)

class UserGameLibrary(Base):
    __tablename__ = "tbl_UserGameLibrary"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("tbl_Users.id"), index=True, nullable=False)
    appid: Mapped[int] = mapped_column(Integer, ForeignKey("tbl_SteamGames.appid"), index=True, nullable=False)
    library_wishlist: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    hidden: Mapped[int] = mapped_column(Integer, default=0)

class UserComments(Base):
    __tablename__ = "tbl_UserComments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("tbl_Users.id"), index=True, nullable=False)
    appid: Mapped[int] = mapped_column(Integer, ForeignKey("tbl_SteamGames.appid"), index=True, nullable=False)
    comment: Mapped[str] = mapped_column(String, index=False, nullable=False)

