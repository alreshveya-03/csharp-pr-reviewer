using System;
using System.Data.SqlClient;
using System.Threading.Tasks;

public class UserService
{
    private string connectionString =
        "Server=localhost;Database=Users;User Id=sa;Password=admin123";

    public async Task<bool> Login(string username, string password)
    {
        SqlConnection connection = new SqlConnection(connectionString);

        connection.Open();

        string query =
            "SELECT * FROM Users WHERE Username='" +
            username +
            "' AND Password='" +
            password +
            "'";

        SqlCommand command = new SqlCommand(query, connection);

        var result = command.ExecuteReader();

        Console.WriteLine(username.Length);

        if (result.HasRows)
        {
            return true;
        }

        return false;
    }
}
