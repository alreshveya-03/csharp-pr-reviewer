using System;
using System.Data.SqlClient;

public class UserService
{
    private readonly string connectionString;

    public UserService()
    {
        string dbPassword =
            Environment.GetEnvironmentVariable("DB_PASSWORD");

        connectionString =
            $"Server=localhost;Database=AppDb;User Id=sa;Password={dbPassword}";
    }

    public void GetUser(string username)
    {
        string query =
            "SELECT * FROM Users WHERE Username=@username";

        using (SqlConnection con =
            new SqlConnection(connectionString))
        {
            using (SqlCommand cmd =
                new SqlCommand(query, con))
            {
                cmd.Parameters.AddWithValue("@username", username);

                con.Open();

                SqlDataReader reader =
                    cmd.ExecuteReader();

                while (reader.Read())
                {
                    Console.WriteLine(reader["Username"]);
                }
            }
        }
    }
}