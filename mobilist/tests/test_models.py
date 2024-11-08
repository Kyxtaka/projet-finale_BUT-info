import models 


def test_user_creation():
    """
    Tests dela classe USER 
    """
    proprio = models.Proprietaire(1,"John","Kevin","exemple@mail.com")
    user = models.User("exemple@mail.com", "123", "admin",1)
    
    