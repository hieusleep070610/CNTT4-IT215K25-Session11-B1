from fastapi import FastAPI, status, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, Session

DATABASE_URL = "mysql+pymysql://root:password@localhost:3306/parking_db"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


class ParkingSlotModel(Base):
    __tablename__ = "parking_slots"

    id = Column(Integer, primary_key=True)
    slot_code = Column(String(50), unique=True, nullable=False)
    zone_name = Column(String(255), nullable=False)
    max_weight = Column(Integer, nullable=False)
    is_available = Column(Boolean, default=True)


Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI()


@app.post("/parking-slots")
def create_parking_slot(
    slot_code: str,
    zone_name: str,
    max_weight: int,
    db: Session = Depends(get_db)
):

    check = (
        db.query(ParkingSlotModel)
        .filter(ParkingSlotModel.slot_code == slot_code)
        .first()
    )

    if check:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mã vị trí đỗ đã tồn tại"
        )

    if not zone_name.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tên khu vực không được để trống"
        )

    if max_weight <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tải trọng phải lớn hơn 0"
        )

    new_slot = ParkingSlotModel(
        slot_code=slot_code,
        zone_name=zone_name,
        max_weight=max_weight
    )

    db.add(new_slot)
    db.commit()
    db.refresh(new_slot)

    return new_slot


@app.get("/parking-slots")
def get_all_parking_slots(
    db: Session = Depends(get_db)
):
    return db.query(ParkingSlotModel).all()


@app.get("/parking-slots/{slot_id}")
def get_parking_slot_by_id(
    slot_id: int,
    db: Session = Depends(get_db)
):

    slot = (
        db.query(ParkingSlotModel)
        .filter(ParkingSlotModel.id == slot_id)
        .first()
    )

    if not slot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy vị trí đỗ xe"
        )

    return slot
