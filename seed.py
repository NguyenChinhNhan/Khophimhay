
from app import create_app, db
from app.models import Movie

app = create_app()

with app.app_context():
    movie1 = Movie(title="Phim Hài 2024", description="Một bộ phim hài vui nhộn", filename="phimhai.mp4")
    movie2 = Movie(title="Phim Hành Động", description="Gay cấn đến phút cuối", filename="hanhdong.mp4")

    db.session.add_all([movie1, movie2])
    db.session.commit()
    print("Đã thêm phim mẫu vào CSDL")
