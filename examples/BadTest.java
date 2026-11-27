public class BadTest {

    @Test
    public void test1() throws Exception {
        driver.get("https://prod.example.com/login");
        driver.findElement(By.id("email")).sendKeys("tanya@test.com");
        driver.findElement(By.id("password")).sendKeys("Qwerty123");
        driver.findElement(By.xpath("//button[1]")).click();
        Thread.sleep(5000);
        driver.findElement(By.id("profile")).click();
    }

    @Test
    public void test2() throws Exception {
        driver.get("https://prod.example.com/login");
        driver.findElement(By.id("email")).sendKeys("tanya@test.com");
        driver.findElement(By.id("password")).sendKeys("Qwerty123");
        driver.findElement(By.xpath("//button[1]")).click();
        Thread.sleep(5000);
        try {
            String name = driver.findElement(By.id("name")).getText();
            assertTrue(name != null);
        } catch (Exception e) {
        }
    }
}