import assert from 'node:assert';
import { Builder, Browser, By, Key, until } from 'selenium-webdriver';


describe('Testes do Módulo de Login', function() {
    it('Deve permitir o login quando usar credenciais vaálidas', async () => { 
        // Arrange
        const driver = new Builder().forBrowser(Browser.CHROME).build();
        await driver.get('https://quick-notes.club/');
      
        // Act
        await driver.findElement(By.id('login-email')).sendKeys('hugoscaper@gmail.com');
        await driver.findElement(By.id('login-password')).sendKeys('Black3774.' ,Key.RETURN);
        
        // Assert
        await driver.wait(until.elementIsVisible(driver.findElement(By.id('user-name'))), 5000);
        const saudacao = await driver.findElement(By.id('user-name')).getText();
        assert.equal(saudacao, 'Hi, Hugo Moreira');
        await driver.quit();
      
    });
});