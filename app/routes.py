from app.utils import send_verify_email
from flask import render_template
from app.models import Movie
from flask import current_app as app
import os
from flask import request, redirect, url_for, flash, session
from config import Config
from flask_bcrypt import Bcrypt
from flask_login import login_user, logout_user, login_required, current_user
import random, smtplib
from app.models import User, db
from app.utils import send_verify_email
from werkzeug.security import check_password_hash
from .models import Admin
from .models import Report
from app.models import Post, User
from werkzeug.utils import secure_filename
from .models import Actor,Director,UserGroup,Genre
@app.route('/')
def index():
    movies = Movie.query.all()
    logged_in = current_user.is_authenticated
    return render_template('index.html', movies=movies,  logged_in=current_user.is_authenticated)
@app.route("/watch/<int:movie_id>")
def watch(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    print("🎬 Phát phim:", movie.filename)
    print("🎬 Tên file từ database:", movie.filename)
    return render_template("watch.html", movie=movie)



bcrypt = Bcrypt()

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        print("📥 Nhận form đăng ký")
        username = request.form['username']
        email = request.form['email'].lower()
        password = request.form['password']

        if not email.endswith('@gmail.com'):
            flash('❌ Chỉ chấp nhận đăng ký bằng Gmail!')
            return redirect(url_for('register'))

        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()

        if existing_user:
            flash('❌ Tên đăng nhập hoặc email đã tồn tại!')
            return redirect(url_for('register'))

        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        code = f"{random.randint(100000, 999999)}"

        user = User(
            username=username,
            email=email,
            password=hashed_pw,
            verify_code=code
        )
        db.session.add(user)
        db.session.commit()

        # Gửi mã xác nhận
        send_verify_email(email, code)

        # 👉 Lưu email vào session để xác minh
        session['verify_email'] = email
        print(f"✅ Đăng ký thành công cho: {email}, chuyển sang verify")

        flash('✅ Đăng ký thành công! Vui lòng kiểm tra email để xác thực.')
        return redirect(url_for('verify'))
        print("✅ Đăng ký thành công, lưu vào session:", session.get('verify_email'))
    return render_template('register.html')
@app.route('/verify', methods=['GET', 'POST'])
def verify():
    email = session.get('verify_email')
    print("🧐 Truy cập /verify, email trong session:", email)
    if not email:
        flash('Không có email xác minh. Vui lòng đăng ký lại.')
        return redirect(url_for('register'))

    if request.method == 'POST':
        code = request.form.get('code')
        user = User.query.filter_by(email=email).first()
        if user and user.verify_code == code:
            user.is_verified = True
            db.session.commit()
            session.pop('verify_email', None)
            flash('✅ Xác minh thành công! Hãy đăng nhập.')
            return redirect(url_for('login'))
        else:
            flash('❌ Mã xác nhận không đúng.')

    return render_template('verify.html')
@app.route('/login', methods=['GET', 'POST'])
#dangnhap
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Kiểm tra có phải admin không
        admin = Admin.query.filter_by(username=username).first()
        if admin and check_password_hash(admin.password, password):
            session['admin_logged_in'] = True  # đánh dấu trong session
            flash('✅ Đăng nhập với tư cách quản trị viên.')
            return redirect(url_for('admin_dashboard'))

        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            if user.is_verified:
                login_user(user)
                flash('✅ Đăng nhập thành công!')
                return redirect(url_for('index'))
            else:
                flash('❌ Tài khoản chưa xác thực.')
        else:
            flash('❌ Tên đăng nhập hoặc mật khẩu không đúng.')

    return render_template('login.html')
@app.route('/forgot', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email'].lower()
        user = User.query.filter_by(email=email).first()
        if user:
            code = f"{random.randint(100000, 999999)}"
            user.verify_code = code
            db.session.commit()

            send_verify_email(user.email, code)  # Đã có sẵn trong utils.py
            session['reset_email'] = user.email
            flash('✅ Mã xác nhận đã được gửi tới email của bạn.')
            return redirect(url_for('reset_password'))
        else:
            flash('❌ Email không tồn tại trong hệ thống.')
    return render_template('forgot.html')
@app.route('/reset', methods=['GET', 'POST'])
def reset_password():
    email = session.get('reset_email')
    if not email:
        flash('Vui lòng thực hiện lại quy trình quên mật khẩu.')
        return redirect(url_for('forgot_password'))

    if request.method == 'POST':
        code = request.form.get('code')
        new_password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and user.verify_code == code:
            hashed_pw = bcrypt.generate_password_hash(new_password).decode('utf-8')
            user.password = hashed_pw
            user.verify_code = None
            db.session.commit()
            flash('✅ Mật khẩu đã được cập nhật. Bạn có thể đăng nhập lại.')
            return redirect(url_for('login'))
        else:
            flash('❌ Mã xác nhận không đúng.')

    return render_template('reset.html')





@app.route("/admin")
def admin_dashboard():
    if not session.get("admin_logged_in"):
        flash("❌ Không có quyền truy cập!", "danger")
        return redirect(url_for("login"))

    users = User.query.all()
    movies = Movie.query.all()
    return render_template("admin/dashboard.html", users=users, movies=movies)
@app.route("/admin/reports")
def admin_reports():
    if not session.get("admin_logged_in"):
        flash("❌ Không có quyền truy cập!", "danger")
        return redirect(url_for("login"))

    reports = Report.query.all()  # Cần có model Report
    return render_template("admin/reports.html", reports=reports)
@app.route('/admin/posts')
def admin_posts():
    posts = Post.query.all()
    return render_template('admin/post/posts.html', posts=posts)

@app.route('/admin/my-posts')
def admin_my_posts():
    my_posts = Post.query.filter_by(author_id=session.get('admin_id')).all()
    return render_template('admin/post/my_posts.html', my_posts=my_posts)

@app.route('/admin/create-post', methods=['GET', 'POST'])
def admin_create_post():
    if request.method == 'POST':
        # Xử lý tạo bài viết
        pass
    return render_template('admin/post/create_post.html')
@app.route("/admin/movies/create", methods=["GET", "POST"])
def admin_create_movie():
    if not session.get("admin_logged_in"):
        flash("❌ Bạn cần đăng nhập với quyền quản trị!", "danger")
        return redirect(url_for("login"))

    genres = Genre.query.all()

    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        genre_id = request.form.get("genre_id")
        file = request.files["file"]

        if file and file.filename.endswith(".mp4"):
            filename = secure_filename(file.filename)

            # Đảm bảo thư mục tồn tại
            upload_folder = os.path.join("static", "uploads", "movies")
            os.makedirs(upload_folder, exist_ok=True)

            filepath = os.path.join(upload_folder, filename)
            print("🎬 Đường dẫn lưu:", filepath)
            print("🎬 Tên file lưu:", filename)
            print("👉 Đường dẫn tuyệt đối:", os.path.abspath(filepath))

            file.save(filepath)

            # Lưu tên file và các thông tin khác vào CSDL
            new_movie = Movie(
                title=title,
                description=description,
                filename=filename,
                genre_id=genre_id
            )
            db.session.add(new_movie)
            db.session.commit()

            flash("✅ Phim đã được tải lên!", "success")
            return redirect(url_for("admin_movies"))
        else:
            flash("❌ Vui lòng chọn file .mp4 hợp lệ!", "danger")


    return render_template("admin/movies/create_movie.html", genres=genres)

@app.route("/admin/movies")
def admin_movies():
    if not session.get("admin_logged_in"):
        flash("❌ Bạn cần đăng nhập với quyền quản trị!", "danger")
        return redirect(url_for("login"))

    page = request.args.get('page', 1, type=int)
    genre_id = request.args.get("genre_id", type=int)

    query = Movie.query
    if genre_id:
        query = query.filter_by(genre_id=genre_id)

    movies = query.order_by(Movie.id.desc()).paginate(page=page, per_page=5)
    genres = Genre.query.all()

    return render_template(
        "admin/movies/movie_list.html",movies=movies,genres=genres,selected_genre=genre_id
    )

@app.route('/admin/movies/edit/<int:movie_id>', methods=['GET', 'POST'])
def edit_movie(movie_id):
    if not session.get("admin_logged_in"):
        return redirect(url_for("login"))

    movie = Movie.query.get_or_404(movie_id)

    if request.method == 'POST':
        movie.title = request.form['title']
        movie.description = request.form['description']
        db.session.commit()
        flash("✅ Đã cập nhật phim!", "success")
        return redirect(url_for('admin_movies'))

    return render_template('admin/movies/edit_movie.html', movie=movie)


@app.route('/admin/movies/delete/<int:movie_id>')
def delete_movie(movie_id):
    if not session.get("admin_logged_in"):
        return redirect(url_for("login"))

    movie = Movie.query.get_or_404(movie_id)

    # 🗑 Xóa file video nếu có
    if movie.filename:
        video_path = os.path.join('static', 'uploads', 'movies', movie.filename)
        if os.path.exists(video_path):
            os.remove(video_path)

    # 🗑 Xoá dữ liệu trong CSDL
    db.session.delete(movie)
    db.session.commit()
    flash("🗑 Phim và file video đã bị xoá!", "info")
    return redirect(url_for('admin_movies'))


@app.route("/admin/actors")
def admin_actors():
    search = request.args.get("search", "")
    page = request.args.get("page", 1, type=int)

    query = Actor.query
    if search:
        query = query.filter(Actor.name.ilike(f"%{search}%"))

    pagination = query.paginate(page=page, per_page=5)
    actors = pagination.items

    return render_template("admin/actors/actor_list.html", actors=actors, pagination=pagination, search=search)

@app.route("/admin/actors/create", methods=["GET", "POST"])
def admin_create_actor():
    if not session.get("admin_logged_in"):
        flash("Bạn cần đăng nhập với quyền admin.", "danger")
        return redirect(url_for("login"))

    if request.method == "POST":
        name = request.form["name"]
        bio = request.form["bio"]
        avatar_file = request.files["avatar"]

        if avatar_file and avatar_file.filename.endswith(('.jpg', '.jpeg', '.png')):
            filename = secure_filename(avatar_file.filename)
            avatar_path = os.path.join("static/uploads/actors", filename)
            avatar_file.save(avatar_path)

            actor = Actor(name=name, bio=bio, avatar=filename)
            db.session.add(actor)
            db.session.commit()

            flash("✅ Đã thêm diễn viên!", "success")
            return redirect(url_for("admin_actors"))
        else:
            flash("❌ Chỉ hỗ trợ ảnh JPG, JPEG, PNG!", "danger")

    return render_template("admin/actors/create_actor.html")
@app.route("/admin/actors/edit/<int:actor_id>", methods=["GET", "POST"])
def edit_actor(actor_id):
    actor = Actor.query.get_or_404(actor_id)

    if request.method == "POST":
        actor.name = request.form["name"]
        actor.bio = request.form["bio"]

        avatar_file = request.files.get("avatar")
        if avatar_file and avatar_file.filename:
            filename = secure_filename(avatar_file.filename)
            avatar_path = os.path.join("static/uploads/actors", filename)
            avatar_file.save(avatar_path)
            actor.avatar = filename

        db.session.commit()
        flash("✅ Đã cập nhật diễn viên!", "success")
        return redirect(url_for("admin_actors"))

    return render_template("admin/actors/edit_actor.html", actor=actor)
@app.route("/admin/actors/delete/<int:actor_id>")
def delete_actor(actor_id):
    actor = Actor.query.get_or_404(actor_id)

    # Nếu muốn xoá luôn file ảnh:
    try:
        os.remove(os.path.join("static/uploads/actors", actor.avatar))
    except Exception:
        pass  # Bỏ qua nếu file không tồn tại

    db.session.delete(actor)
    db.session.commit()
    flash("🗑 Diễn viên đã bị xoá.", "warning")
    return redirect(url_for("admin_actors"))

@app.route('/admin/directors/create', methods=['GET', 'POST'])
def admin_create_director():
    if not session.get("admin_logged_in"):
        flash("❌ Bạn cần đăng nhập với quyền quản trị!", "danger")
        return redirect(url_for("login"))

    if request.method == "POST":
        name = request.form['name']
        bio = request.form['bio']
        avatar_file = request.files['avatar']

        filename = None
        if avatar_file and avatar_file.filename:
            filename = secure_filename(avatar_file.filename)
            avatar_path = os.path.join("static/uploads/directors", filename)
            avatar_file.save(avatar_path)

        new_director = Director(name=name, bio=bio, avatar=filename)
        db.session.add(new_director)
        db.session.commit()
        flash("✅ Đạo diễn đã được thêm!", "success")
        return redirect(url_for('admin_directors'))

    return render_template("admin/directors/create_director.html")
@app.route('/admin/directors')
def admin_directors():
    # Lấy số trang và chuỗi tìm kiếm từ query string
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('q', '').strip()

    # Bắt đầu query từ toàn bộ bảng
    query = Director.query

    # Nếu có tìm kiếm
    if search_query:
        query = query.filter(Director.name.ilike(f"%{search_query}%"))

    # Phân trang
    pagination = query.paginate(page=page, per_page=5)
    directors = pagination.items
    total_pages = pagination.pages

    # Truyền các biến cần thiết vào template
    return render_template(
        'admin/directors/director_list.html',directors=directors,page=page,total_pages=total_pages,search_query=search_query
    )

@app.route('/admin/directors/edit/<int:director_id>', methods=['GET', 'POST'])
def edit_director(director_id):
    director = Director.query.get_or_404(director_id)

    if request.method == 'POST':
        director.name = request.form['name']
        director.bio = request.form['bio']
        avatar_file = request.files['avatar']

        if avatar_file and avatar_file.filename:
            filename = secure_filename(avatar_file.filename)
            avatar_path = os.path.join("static/uploads/directors", filename)
            avatar_file.save(avatar_path)
            director.avatar = filename

        db.session.commit()
        flash("✅ Đã cập nhật đạo diễn!", "success")
        return redirect(url_for('admin_directors'))

    return render_template("admin/directors/edit_director.html", director=director)
@app.route('/admin/directors/delete/<int:director_id>')
def delete_director(director_id):
    director = Director.query.get_or_404(director_id)
    db.session.delete(director)
    db.session.commit()
    flash("🗑 Đã xoá đạo diễn!", "success")
    return redirect(url_for('admin_directors'))
@app.route("/admin/users")
def admin_users():
    if not session.get("admin_logged_in"):
        flash("❌ Bạn cần đăng nhập với quyền quản trị!", "danger")
        return redirect(url_for("login"))

    search = request.args.get("q", "")
    page = request.args.get("page", 1, type=int)
    per_page = 10

    query = User.query
    if search:
        query = query.filter((User.username.ilike(f"%{search}%")) | (User.email.ilike(f"%{search}%")))

    pagination = query.order_by(User.id.desc()).paginate(page=page, per_page=per_page)
    users = pagination.items

    return render_template("admin/users/list_users.html", users=users, pagination=pagination, search=search)
@app.route("/admin/users/edit/<int:user_id>", methods=["GET", "POST"])
def edit_user(user_id):
    if not session.get("admin_logged_in"):
        flash("❌ Bạn cần đăng nhập với quyền quản trị!", "danger")
        return redirect(url_for("login"))

    user = User.query.get_or_404(user_id)


    if request.method == "POST":
        user.username = request.form["username"]
        user.email = request.form["email"]
        user.role = request.form["role"]
        user.group_id = request.form.get("group_id")

        avatar_file = request.files.get("avatar")
        if avatar_file and avatar_file.filename:
            filename = secure_filename(avatar_file.filename)
            filepath = os.path.join("static/uploads/avatars", filename)
            avatar_file.save(filepath)
            user.avatar = filename  # avatar là tên file lưu

        db.session.commit()
        flash("✅ Cập nhật người dùng thành công!", "success")
        return redirect(url_for("admin_users"))

    return render_template("admin/users/edit_user.html", user=user)

@app.route("/admin/users/delete/<int:user_id>")
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash("🗑 Người dùng đã bị xoá!", "warning")
    return redirect(url_for("admin_users"))

@app.route("/admin/user-groups", methods=["GET", "POST"])
def admin_user_groups():
    if not session.get("admin_logged_in"):
        flash("❌ Bạn cần đăng nhập với quyền quản trị!", "danger")
        return redirect(url_for("login"))

    if request.method == "POST":
        name = request.form["name"]
        description = request.form["description"]

        new_group = UserGroup(name=name, description=description)
        db.session.add(new_group)
        db.session.commit()
        flash("✅ Nhóm người dùng đã được tạo!", "success")
        return redirect(url_for("admin_user_groups"))

    groups = UserGroup.query.all()
    return render_template("admin/users/user_groups.html", groups=groups)

# 📋 Danh sách thể loại
@app.route("/admin/genres")
def admin_genres():
    if not session.get("admin_logged_in"):
        flash("❌ Cần quyền admin để truy cập", "danger")
        return redirect(url_for("login"))

    search = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    per_page = 5

    query = Genre.query
    if search:
        query = query.filter(Genre.name.ilike(f"%{search}%"))

    pagination = query.paginate(page=page, per_page=per_page)
    genres = pagination.items

    return render_template("admin/genre/genre_list.html", genres=genres, pagination=pagination, search=search)

# ➕ Tạo thể loại mới
@app.route("/admin/genres/create", methods=["GET", "POST"])
def admin_create_genre():
    if request.method == "POST":
        name = request.form["name"]
        description = request.form["description"]

        genre = Genre(name=name, description=description)
        db.session.add(genre)
        db.session.commit()
        flash("✅ Thể loại đã được thêm!", "success")
        return redirect(url_for("admin_genres"))

    return render_template("admin/genre/create_genre.html")


# ✏️ Sửa thể loại
@app.route("/admin/genres/edit/<int:genre_id>", methods=["GET", "POST"])
def admin_edit_genre(genre_id):
    genre = Genre.query.get_or_404(genre_id)

    if request.method == "POST":
        genre.name = request.form["name"]
        genre.description = request.form["description"]
        db.session.commit()
        flash("✅ Đã cập nhật thể loại!", "success")
        return redirect(url_for("admin_genres"))

    return render_template("admin/genres/edit_genre.html", genre=genre)


# 🗑 Xóa thể loại
@app.route("/admin/genres/delete/<int:genre_id>")
def admin_delete_genre(genre_id):
    genre = Genre.query.get_or_404(genre_id)
    db.session.delete(genre)
    db.session.commit()
    flash("🗑 Đã xoá thể loại!", "warning")
    return redirect(url_for("admin_genres"))









@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Đã đăng xuất!')
    return redirect(url_for('login'))
@app.route('/admin/logout')
def logout_admin():
    session.pop('admin_logged_in', None)
    flash('✅ Đã đăng xuất khỏi quản trị viên.')
    return redirect(url_for('login'))
@app.route('/dev/delete_all_users')
def delete_all_users():
    User.query.delete()
    db.session.commit()
    return "✅ Đã xóa toàn bộ user."
@app.route("/test_video")
def test_video():
    return '''
    <video controls width="400">
        <source src="/static/uploads/movies/New_Type_of_Hero_X.mp4" type="video/mp4">
        Không phát được video.
    </video>
    '''
