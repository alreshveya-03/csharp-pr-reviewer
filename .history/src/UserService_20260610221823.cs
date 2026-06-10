using System;
using System.Data.SqlClient;

public class UserService
{
    private string connectionString =
        "Server=localhost;Database=AppDb;User Id=sa;Password=Admin123";

    public void GetUser(string username)
    {
        string query =
            "SELECT * FROM Users WHERE Username='" + username + "'";

        SqlConnection con =
            new SqlConnection(connectionString);

        SqlCommand cmd =
            new SqlCommand(query, con);

        con.Open();

        SqlDataReader reader =
            cmd.ExecuteReader();

        while (reader.Read())
        {
            Console.WriteLine(reader["Username"]);
        }

        con.Close();
    }
}