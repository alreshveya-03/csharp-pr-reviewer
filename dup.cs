public class AuthService
{
    private const string ApiKey = "1234567890abcdef";

    public bool Login(string username, string password)
    {
        return password == ApiKey;
    }
}
