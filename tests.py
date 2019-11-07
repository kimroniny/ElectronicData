from datetime import datetime, timedelta
from app.models import User, Resource, Certs
from app import db, app
import unittest, os, pathlib


class UserModelCase(unittest.TestCase):
    def setUp(self):
        # create sqlite in memory
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_password_hashing(self):
        u = User(username='susan')
        u.set_password('cat')
        self.assertFalse(u.check_password('dog'))
        self.assertTrue(u.check_password('cat'))

    def test_res(self):
        u = User(username='asdf', email='asdf@qq.com')
        res = Resource(body="hello")
        res.issuer = u
        db.session.add(res)
        db.session.commit()
        users = User.query.all()
        self.assertEqual(users[0].resources[0].body, 'hello')
        self.assertEqual(users[0].resources[0].issuer.username, 'asdf')
        self.assertEqual(users[0].resources.count(), 1)

    def test_buy(self):
        u1 = User(username='asdf', email='asdf@qq.com')
        res = Resource(body="hello")
        res.issuer = u1
        u2 = User(username='qwer')
        db.session.add(u1)
        db.session.add(u2)
        db.session.add(res)
        db.session.commit()

        u2.buy_res(res)
        db.session.commit()
        self.assertEqual(Certs.query.all()[0].payer_id, 2)
        

    def test_transfer(self):
        u1 = User(username='asdf', email='asdf@qq.com')
        res = Resource(body="hello")
        res.issuer = u1
        u2 = User(username='qwer')
        u3 = User(username='tyui')
        db.session.add(u1)
        db.session.add(u2)
        db.session.add(u3)
        db.session.add(res)
        db.session.commit()
        u2.buy_res(res)
        db.session.commit()
        cert = Certs.query.filter_by(payer_id=u2.id, resource_id=res.id).first()
        u3.obtain_cert(cert)
        db.session.commit()
        self.assertEqual(Certs.query.all()[0].payer_id, 2)
        self.assertEqual(len(cert.query.all()), 2)
        pass
    
    def test_delete(self):
        u1 = User(username='asdf', email='asdf@qq.com')
        res = Resource(body="hello")
        res.issuer = u1
        db.session.add(u1)
        db.session.add(res)
        db.session.commit()
        self.assertEqual(u1.id, 1)
        self.assertEqual(res.id, 1)
        db.session.delete(u1)
        # db.session.commit()
        self.assertTrue(len(User.query.all())==0)
        self.assertTrue(len(Resource.query.all())==1)
        # self.assertEqual(res.id, 1)
        # self.assertEqual(res.body, 'hello')
    
    def test_in(self):
        u1 = User(username='asdf', email='asdf@qq.com')
        res = Resource(body="hello")
        res.issuer = u1
        u2 = User(username='we')
        res2 = Resource(body='hello u2')
        res2.issuer = u2
        u2.buy_res(res)
        db.session.add(u1)
        db.session.add(res)
        db.session.commit()
        ress = Resource.query.filter(
            ~Resource.payer.any(User.id==u2.id)
        ).all()
        # .filter(
        #     Certs.payer_id!=u2.id
        # )
        print(Resource.query.outerjoin(Certs).all())
        ress = Resource.query.outerjoin(Certs).all()
        self.assertTrue((len(ress)==2))
    
    def test_filterBy(self):
        u1 = User(username='asdf', email='asdf@qq.com')
        res = Resource(body="hello")
        res.issuer = u1
        u2 = User(username='we')
        res2 = Resource(body='hello u2')
        res2.issuer = u2
        u2.buy_res(res)
        u3 = User(username='rt')
        db.session.add(u1)
        db.session.add(res)
        db.session.add(u3)
        db.session.commit()
        u3.obtain_cert(
            Certs.query.filter_by(resource_id=res.id, payer_id=u2.id, transfer_id=None).first()
        )
        self.assertEqual(Certs.query.get(1).transfer_id, u3.id)
        certs = Certs.query.filter_by(transfer_id=None)
        self.assertEqual(certs.count(), 1)

    def test_resoperator(self):
        u1 = User(username='asdf', email='asdf@qq.com')
        res = Resource(body="hello")
        res.issuer = u1
        u2 = User(username='we')
        res2 = Resource(body='hello u2')
        res2.issuer = u2
        u2.buy_res(res)
        u3 = User(username='rt')
        db.session.add(u1)
        db.session.add(res)
        db.session.add(u2)
        db.session.add(res2)
        db.session.add(u3)
        db.session.commit()
        u3.obtain_cert(
            Certs.query.filter_by(resource_id=res.id, payer_id=u2.id, transfer_id=None).first()
        )
            
        # query = Resource.query.outerjoin(Certs).filter(
        #     Certs.payer_id==u2.id
        # )
        res_bought = Resource.query.outerjoin(Certs).filter(
            Certs.payer_id==u2.id
        ).all()
        self.assertEqual(len(res_bought), 1)

        res_bought_ex_trans = Resource.query.outerjoin(Certs).filter(
            Certs.payer_id==u2.id, Certs.transfer_id==None
        ).all()
        self.assertEqual(len(res_bought_ex_trans), 0)

        res_transfer = Resource.query.join(Certs).filter(
            Certs.payer_id==u2.id, Certs.transfer_id!=None
        ).all()
        self.assertEqual(len(res_transfer), 1)

    def test_path(self):
        dirs = os.path.join(app.config['RES_FILE_PATH'], '1')
        path = pathlib.Path(dirs)
        self.assertFalse(
            path.exists()
        )
        os.makedirs(dirs)
        self.assertTrue(
            path.exists()
        )
        self.assertFalse(
            path.is_file()
        )

if __name__ == '__main__':
    unittest.main(verbosity=2)
