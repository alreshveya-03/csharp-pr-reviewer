using System;

public class LoginService
{
    public void Login(string username, string password)
    {
        string query =
            "SELECT * FROM Users WHERE Username='" +
            username +
            "' AND Password='" +
            password + "'";

        Console.WriteLine(query);
    }
}
