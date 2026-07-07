from fastapi import FastAPI, status, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker, Session

DATABASE_URL = "mysql+pymysql://root:password@localhost:3306/ecommerce_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ShipmentModel(Base):
    __tablename__ = "shipments"
    id = Column(Integer, primary_key=True)
    tracking_number = Column(String(50), unique=True, nullable=False)
    status = Column(String(50), default="PREPARING")

Base.metadata.create_all(bind=engine)
# Hàm Dependency cung cấp Database Session cho API
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI()
@app.post('/shipment')
# 
def create_shipment( tracking_number: str, db:Session = Depends(get_db)):
    try:
        check= db.query(ShipmentModel).filter(tracking_number == ShipmentModel.tracking_number).first()
        if check :
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail ="Mã đơn này đã được khởi tạo trước đó")
        new_shipment = ShipmentModel(
            tracking_number = tracking_number
        )
        db.add(new_shipment)
        db.commit() 
        db.refresh(new_shipment)
        return new_shipment
    except Exception :
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi hệ thống: {str(Exception)}"
        )
@app.get("/shipment")
def get_shipment(db:Session = Depends(get_db)):
    shipment = db.query(ShipmentModel).all()
    return shipment