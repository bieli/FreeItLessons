from menu import Menu, MenuItem

# Add two items to our main menu
Menu.add_item("main", MenuItem("Tools",
                               reverse("myapp.views.tools"),
                               weight=10,
                               icon="tools"))

Menu.add_item("main", MenuItem("Reports",
                               reverse("myapp.views.reports"),
                               weight=20,
                               icon="report"))


# Define children for the my account menu
myaccount_children = (
    MenuItem("Edit Profile",
             reverse("accounts.views.editprofile"),
             weight=10,
             icon="user"),
    MenuItem("Admin",
             reverse("admin:index"),
             weight=80,
             separator=True,
             check=lambda request: request.user.is_superuser),
    MenuItem("Logout",
             reverse("accounts.views.logout"),
             weight=90,
             separator=True,
             icon="user"),
)

# Add a My Account item to our user menu
Menu.add_item("user", MenuItem("My Account",
                               reverse("accounts.views.myaccount"),
                               weight=10,
                               children=myaccount_children))


