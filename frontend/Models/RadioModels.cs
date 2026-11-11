// Re-exporting Domain Entities under frontend.Models for seamless compatibility
global using Station = frontend.Domain.Entities.Station;
global using FilterOptionsResponse = frontend.Domain.Entities.FilterOptionsResponse;
global using UserPreferences = frontend.Domain.Entities.UserPreferences;
global using TrackMetadata = frontend.Domain.Entities.TrackMetadata;
global using RadioBroadcastMessage = frontend.Domain.Entities.RadioBroadcastMessage;

namespace frontend.Models;
