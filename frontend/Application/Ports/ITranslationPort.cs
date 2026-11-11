namespace frontend.Application.Ports;

/// <summary>
/// Puerto abstracto para la internacionalización y traducción de textos.
/// Autor: Hugo Francisco Luis Inclan (c) 2026.
/// </summary>
public interface ITranslationPort
{
    string CurrentLanguage { get; set; }
    string Translate(string key);
}
