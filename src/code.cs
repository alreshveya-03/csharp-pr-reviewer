using System;
using System.Data.SqlClient;

namespace DemoApplication
{
    public class LoginService
    {
        private string connectionString =
            "Server=localhost;Database=AppDb;User Id=sa;Password=Admin@123;";

        public bool Login(string username, string password)
        {
            string query =
                "SELECT * FROM Users WHERE Username='" + username +
                "' AND Password='" + password + "'";

            SqlConnection connection =
                new SqlConnection(connectionString);

            SqlCommand command =
                new SqlCommand(query, connection);

            connection.Open();

            SqlDataReader reader =
                command.ExecuteReader();

            bool result = reader.HasRows;

            connection.Close();

            return result;
        }

        public void PrintUser(string name)
        {
            Console.WriteLine("Welcome " + name);
        }
    }
}
// Test PR by Yazhini