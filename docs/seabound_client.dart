// Sample Flutter client for the fish forecast API. NOT compiled or run (no Flutter SDK where this was written):
// treat it as a starting point and check the calls against the package versions you use.
//
// pubspec.yaml needs: http, latlong2, flutter_map. (Add intl if you want nicer time formatting.)
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:http/http.dart' as http;
import 'package:latlong2/latlong.dart';

/// Use the GitHub Pages address (see seabound-api.md) once you switch it on.
const fishApiBase = 'https://raw.githubusercontent.com/markeetox/lupita/data/api/v1/';

Color colorFromHex(String hex) => Color(int.parse(hex.substring(1), radix: 16) | 0xFF000000);

class FishApi {
  FishApi({http.Client? client, this.base = fishApiBase}) : _client = client ?? http.Client();
  final String base;
  final http.Client _client;

  /// Turns a path from the API into a full address. Absolute links (a remote photo) are left alone.
  String url(String rel) => rel.startsWith('http') ? rel : '$base$rel';

  Future<Map<String, dynamic>> _getJson(String rel) async {
    final res = await _client.get(Uri.parse(url(rel)));
    if (res.statusCode != 200) throw Exception('Fish API $rel: HTTP ${res.statusCode}');
    return jsonDecode(utf8.decode(res.bodyBytes)) as Map<String, dynamic>;
  }

  Future<FishIndex> index() async => FishIndex.fromJson(await _getJson('index.json'));
  Future<FishDetail> species(String id) async => FishDetail.fromJson(await _getJson('species/$id.json'));
}

class FishIndex {
  FishIndex({required this.generatedUtc, required this.disclaimer, required this.species, required this.attribution, this.conditions});
  final DateTime generatedUtc;
  final String disclaimer;
  final List<FishSummary> species;
  final List<String> attribution;
  final Map<String, dynamic>? conditions; // moon, front, sea

  factory FishIndex.fromJson(Map<String, dynamic> j) => FishIndex(
        generatedUtc: DateTime.parse(j['generated_utc'] as String),
        disclaimer: j['disclaimer'] as String? ?? '',
        species: (j['species'] as List).map((e) => FishSummary.fromJson(e as Map<String, dynamic>)).toList(),
        attribution: (j['attribution'] as List?)?.cast<String>() ?? const [],
        conditions: j['conditions'] as Map<String, dynamic>?,
      );
}

class FishSummary {
  FishSummary({required this.id, required this.name, required this.scientificName, required this.color, required this.imagePath,
      required this.status, required this.message, required this.areaCount, this.heatPng, this.heatBounds});
  final String id, name, scientificName, color, imagePath, status, message;
  final int areaCount;
  final String? heatPng;
  final List<double>? heatBounds; // [west, south, east, north]

  bool get hasAreas => status == 'ok' && areaCount > 0;

  factory FishSummary.fromJson(Map<String, dynamic> j) {
    final heat = j['heat'] as Map<String, dynamic>?;
    return FishSummary(
      id: j['id'] as String, name: j['name'] as String, scientificName: j['scientific_name'] as String? ?? '',
      color: j['color'] as String, imagePath: (j['image'] as Map)['url'] as String,
      status: j['status'] as String, message: j['message'] as String? ?? '', areaCount: j['area_count'] as int? ?? 0,
      heatPng: heat?['png'] as String?,
      heatBounds: (heat?['bounds'] as List?)?.map((e) => (e as num).toDouble()).toList(),
    );
  }
}

class FishDetail {
  FishDetail({required this.name, required this.about, required this.areas, required this.message, required this.status});
  final String name, message, status;
  final Map<String, dynamic> about; // size, diet, behavior, depth, spawning, lifespan, regulations_link ...
  final List<FishArea> areas;

  factory FishDetail.fromJson(Map<String, dynamic> j) {
    final today = j['today'] as Map<String, dynamic>;
    return FishDetail(
      name: j['name'] as String, about: (j['about'] as Map).cast<String, dynamic>(),
      status: today['status'] as String, message: today['message'] as String? ?? '',
      areas: (today['areas'] as List).map((e) => FishArea.fromJson(e as Map<String, dynamic>)).toList(),
    );
  }
}

class FishArea {
  FishArea({required this.id, required this.title, required this.score, required this.confidence, required this.position,
      required this.reasons, required this.details, this.timing, this.sea});
  final String id, title, confidence;
  final double score; // 0..1
  final LatLng position;
  final List<({String tag, String text})> reasons;
  final List<({String label, String value})> details;
  final Map<String, dynamic>? timing; // null: no reliable timing for this fish
  final Map<String, dynamic>? sea; // {level, text}

  /// The best bite window, in the phone's local time, or null.
  ({DateTime start, DateTime end})? get bestWindow {
    final w = timing?['window'] as Map<String, dynamic>?;
    if (w == null) return null;
    return (start: DateTime.parse(w['start'] as String).toLocal(), end: DateTime.parse(w['end'] as String).toLocal());
  }

  factory FishArea.fromJson(Map<String, dynamic> j) {
    final c = (j['coords'] as List).map((e) => (e as num).toDouble()).toList(); // [lon, lat]
    return FishArea(
      id: j['id'] as String, title: j['title'] as String, score: (j['score'] as num).toDouble(), confidence: j['confidence'] as String,
      position: LatLng(c[1], c[0]),
      reasons: (j['reasons'] as List).map((e) => (tag: e['tag'] as String, text: e['text'] as String)).toList(),
      details: (j['details'] as List).map((e) => (label: e['label'] as String, value: e['value'] as String)).toList(),
      timing: j['timing'] as Map<String, dynamic>?, sea: j['sea'] as Map<String, dynamic>?,
    );
  }
}

/// The heat layer for one fish, to put inside a FlutterMap's `children`. Returns an empty widget for fish with no heat.
Widget fishHeatLayer(FishApi api, FishSummary fish, {double opacity = 1.0}) {
  final b = fish.heatBounds, png = fish.heatPng;
  if (b == null || png == null) return const SizedBox.shrink();
  return OverlayImageLayer(overlayImages: [
    OverlayImage(
      bounds: LatLngBounds(LatLng(b[1], b[0]), LatLng(b[3], b[2])), // south-west, north-east
      opacity: opacity,
      imageProvider: NetworkImage(api.url(png)),
    ),
  ]);
}

/// The fish picture for a card or sheet header.
Widget fishPicture(FishApi api, FishSummary fish, {double height = 134}) =>
    Image.network(api.url(fish.imagePath), height: height, fit: BoxFit.contain, errorBuilder: (_, __, ___) => const SizedBox.shrink());
