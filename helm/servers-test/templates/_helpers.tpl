{{- define "chart.name" -}}
{{-   .Chart.Name -}}
{{- end -}}

{{- define "app.fullname" -}}
{{-   if .Values.fullnameOverride -}}
{{-     .Values.fullnameOverride | trunc 53 | trimSuffix "-" -}}
{{-   else -}}
{{-     .Release.Name | trunc 53 | trimSuffix "-" -}}
{{-   end -}}
{{- end -}}

{{- define "chart.image.name" -}}
{{-   .Values.image.name -}}
{{- end -}}
