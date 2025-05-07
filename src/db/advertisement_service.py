import os
from typing import Optional, List, Union
from db.base import SessionLocal, engine, Base
from contextlib import contextmanager
from .models import (
    Advertisement,
    AdvertisementPhoto,
    User
)
from sqlalchemy.orm import (
    Session,
    joinedload
)
from sqlalchemy.sql import exists


# Create the tables (only once)
Base.metadata.create_all(
    bind=engine
)


class AdvertisementDb:
    def __init__(self):
        self.session = SessionLocal()

    async def add_advertisement(
        self,
        user_id: str,
        vehicle_type: str,
        advertisement_type: Optional[str] = None,
        brand: Optional[str] = None,
        model: Optional[str] = None,
        color: Optional[str] = None,
        function: Optional[int] = None,
        insurance: Optional[bool] = None,
        exchange: Optional[bool] = None,
        motor: Optional[int] = None,
        body: Optional[int] = None,
        chassis: Optional[int] = None,
        technical: Optional[int] = None,
        gearbox: Optional[str] = None,
        money: Optional[str] = None,
        photos: Optional[List[str]] = None,
        default_photo: Optional[str] = None,
        more_detail: Optional[str] = None,
    ) -> Advertisement:

        new_ad = Advertisement(
            user_id=user_id,
            brand=brand,
            advertisement_type=advertisement_type,
            vehicle_type=vehicle_type,
            model=model,
            color=color,
            function=function,
            insurance=insurance,
            exchange=exchange,
            motor=motor,
            body=body,
            chassis=chassis,
            technical=technical,
            gearbox=gearbox,
            money=money,
            more_detail=more_detail
        )
        try:
            self.session.add(new_ad)
            self.session.flush()  # Get the ID before commit

            # Handle photos
            if not os.path.exists('ads_photos'):
                os.makedirs('ads_photos')
            new_photos_info = []

            if photos:
                for photo in photos:
                    # Get the highest quality photo
                    file = await photo.get_file()
                    file_path = f"ads_photos/{new_ad.adv_id}_{file.file_id}.jpg"

                    # Save photo to disk
                    await file.download_to_drive(file_path)

                    # Create photo record
                    new_photos_info.append(AdvertisementPhoto(
                        photo_path=file_path,
                        advertisement_id=new_ad.adv_id
                    ))

                self.session.add_all(new_photos_info)
            else:
                if default_photo:
                    new_photo_info= AdvertisementPhoto(
                        photo_path=default_photo,
                        advertisement_id=new_ad.adv_id
                    )
                    self.session.add(new_photo_info)

            self.session.commit()
            return new_ad
        except BaseException as e:
            print(e)
            self.session.rollback()
            raise False

    def get_advertisement_with_photos(self, adv_id: int):
        try:
            advertisement = self.session.query(Advertisement).options(
                joinedload(Advertisement.photos)
            ).filter(Advertisement.adv_id == adv_id).first()
            return advertisement
        except BaseException as e:
            print(e)
            self.session.rollback()
            raise False


    def get_advertisements_with_photos(self, **filters):
        try:
            query = self.session.query(Advertisement).options(joinedload(Advertisement.photos))

            for attr, value in filters.items():
                if hasattr(Advertisement, attr):
                    query = query.filter(getattr(Advertisement, attr) == value)

            return query.all()

        except BaseException as e:
            print(e)
            self.session.rollback()
            raise False

    def check_exist_user(self, user_id: int) -> bool:
        try:
            return self.session.query(
                exists().where(
                    User.user_id == user_id)).scalar()
        except BaseException as e:
            print(e)
            self.session.rollback()
            raise False

    def get_user_by_id(self, user_id: int):
        """جستجو کاربر بر اساس user_id"""
        try:
            return self.session.query(User).filter(User.user_id == user_id).first()
        except BaseException as e:
            print(e)
            self.session.rollback()
            raise False

    def insert_new_user(self,
                        user_id: int,
                        username: str,
                        first_name: Optional[str],
                        last_name: Optional[str],
                        phone_number: Optional[str],
                        submit_username: Optional[str]
                        ) -> bool:
        """Insert new user into database"""
        try:
            new_user = User(
                user_id=user_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                phone_number=phone_number,
                submit_username=submit_username
            )
            self.session.add(new_user)
            self.session.commit()
            return True
        except BaseException as e:
            print(e)
            self.session.rollback()
            raise False

    def insert_new_adver(self,
                         user_id: int,
                         description: str) -> Union[int, None]:
        """Insert new advertisement and return advertisement ID"""
        try:
            new_advertisement = Advertisement(
                user_id=user_id, description=description)
            self.session.add(new_advertisement)
            self.session.commit()
            return new_advertisement.adv_id
        except BaseException as e:
            print(e)
            self.session.rollback()
            raise False

    def get_user_info(self, user_id: int) -> Optional[dict]:
        """Get user information by user_id."""
        try:
            user = self.session.query(User).filter(User.user_id == user_id).first()
            if user:
                return {
                    "user_id": user.user_id,
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "phone_number": user.phone_number,
                    "submit_username": user.submit_username
                }
            return None
        except BaseException as e:
            print(e)
            self.session.rollback()
            raise False

    def get_adv_info(self, adv_id: int) -> Optional[dict]:
        """Get advertisement information by adv_id."""
        try:
            advertisement = self.session.query(Advertisement).filter(
                Advertisement.adv_id == adv_id).first()
            if advertisement:
                return {
                    "adv_id": advertisement.adv_id,
                    "user_id": advertisement.user_id,
                    "inserted_at": advertisement.inserted_at.isoformat()
                }
            return None
        except BaseException as e:
            print(e)
            self.session.rollback()
            raise False

    def check_user_is_admin(self, user_id: int) -> bool:
        try:
            # Query the user by user_id
            user = self.session.query(User).filter(
                User.user_id == user_id).first()

            # If the user exists and is an admin, return True
            if user and user.is_admin:
                return True
            return False
        except Exception as e:
            print(e)
            self.session.rollback()
            raise False

    def update_user_info(
        self,
        user_id: int,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        phone_number: Optional[str] = None,
        username: Optional[str] = None
    ) -> bool:
        try:
            # Get the user from database
            user = self.session.query(User).filter_by(user_id=user_id).first()
            if not user:
                return False

            update_data = {}

            # Validate and prepare update data
            if username is not None:
                update_data['username'] = username

            if first_name is not None:
                update_data['first_name'] = first_name

            if last_name is not None:
                update_data['last_name'] = last_name

            if phone_number is not None:
                update_data['phone_number'] = phone_number

            # Perform the update if there are changes
            if update_data:
                self.session.query(User).filter_by(
                    user_id=user_id).update(update_data)
                self.session.commit()
                return True

            return False

        except Exception as e:
            print(e)
            self.session.rollback()
            raise False
        

    def update_advertisment_info(
        self,
        adv_id: int,
        **kwargs
    ) -> bool:
        """
        Update advertisement info using keyword arguments.

        Args:
            db (Session): SQLAlchemy database session.
            adv_id (int): ID of the advertisement to update.
            **kwargs: Fields and values to update.

        Returns:
            bool: True if update was successful, False otherwise.
        """
        try:
            adv: Optional[Advertisement] = self.session.query(Advertisement).filter_by(adv_id=adv_id).first()

            if not adv:
                return False

            for key, value in kwargs.items():
                if hasattr(adv, key):
                    setattr(adv, key, value)

            self.session.commit()
            return True
        except Exception as e:
            print(e)
            self.session.rollback()
            raise False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()
