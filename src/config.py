"""
Configuration file for dependency report processing
"""

# Directories
INPUT_DIR = "sc"
OUTPUT_DIR = "out"
TEMP_DIR = "temp"

# Columns to remove from initial CSV
COLUMNS_TO_REMOVE = [
    'id',
    'issuesCritical',
    'issuesHigh',
    'issuesMedium',
    'issuesLow',
    'dependenciesWithIssues',
    'projects',
    'latestVersion',
    'latestVersionPublishedDate',
    'firstPublishedDate',
    'isDeprecated'
]

# Prefixes to filter out (internal packages)
FILTER_PREFIXES = [
    'Mobilize.',
    'Artinsoft.',
    'AMG',
    'Snowflake.',
    'Snow.',
    'MSTest.',
    'Microsoft.CodeCoverage.',
    'snowconvert',
    'SnowFlake.Common.',
    'Microsoft.TestPlatform.',
    'Microsoft.NET.Test.',
    'FluentAssertions',
    '@snowflake/',
    '@mobilize/',
    'EtlToDbt',
    'freqSystemDependencies'
]

# License file variations to check
LICENSE_FILES = [
    "LICENSE.md",
    "LICENSE",
    "LICENSE.txt",
    "LICENSE.TXT",
    "LICENSE-MIT",
    "LICENSE-APACHE",
    "license.md",
    "license",
    "license.txt",
    "license-mit",
    "license-apache",
]

# GitHub branches to check
GITHUB_BRANCHES = ["master", "main", "develop" , "feature/phased-migrations/main"]

# Request delays (seconds)
REQUEST_DELAY_NUGET = 2
REQUEST_DELAY_NPM = 1

# Max recursion depth for license search
MAX_RECURSION_DEPTH = 5

# Report title (can be customized)
REPORT_TITLE = "SnowConvert AI - Open Source Libraries"

# Known package license URLs (to avoid HTTP requests for common packages)
KNOWN_LICENSE_URLS = {
    # AWS SDK for .NET
    'AWSSDK.Core': 'https://github.com/aws/aws-sdk-net/blob/master/License.txt',
    'AWSSDK.Redshift': 'https://github.com/aws/aws-sdk-net/blob/master/License.txt',
    'AWSSDK.RedshiftServerless': 'https://github.com/aws/aws-sdk-net/blob/master/License.txt',
    'AWSSDK.S3': 'https://github.com/aws/aws-sdk-net/blob/master/License.txt',
    
    # Google Cloud & APIs
    'Google.Api.Gax': 'https://github.com/googleapis/gax-dotnet/blob/master/LICENSE',
    'Google.Api.Gax.Rest': 'https://github.com/googleapis/gax-dotnet/blob/master/LICENSE',
    'Google.Apis': 'https://github.com/googleapis/google-api-dotnet-client/blob/master/LICENSE',
    'Google.Apis.Auth': 'https://github.com/googleapis/google-api-dotnet-client/blob/master/LICENSE',
    'Google.Apis.Core': 'https://github.com/googleapis/google-api-dotnet-client/blob/master/LICENSE',
    'Google.Apis.Storage.v1': 'https://github.com/googleapis/google-api-dotnet-client/blob/master/LICENSE',
    'Google.Cloud.Storage.V1': 'https://github.com/googleapis/google-cloud-dotnet/blob/master/LICENSE',
    
    # AutoFixture
    'AutoFixture': 'https://github.com/AutoFixture/AutoFixture/blob/master/LICENCE.txt',
    'AutoFixture.Xunit2': 'https://github.com/AutoFixture/AutoFixture/blob/master/LICENCE.txt',
    
    # Antlr
    'Antlr4.Runtime.Standard': 'https://github.com/antlr/antlr4/blob/master/LICENSE.txt',
    
    # ElectronCgi
    'ElectronCgi.DotNet.signed': 'https://github.com/ruidfigueiredo/electron-cgi/blob/master/LICENSE',
    
    # Fare
    'Fare': 'https://github.com/moodmosaic/Fare/blob/master/license.txt',
    
    # Microsoft packages (dotnet/runtime)
    'Microsoft.Bcl': 'https://github.com/dotnet/runtime/blob/master/LICENSE.TXT',
    'Microsoft.Bcl.Async': 'https://github.com/dotnet/runtime/blob/master/LICENSE.TXT',
    'Microsoft.Bcl.Build': 'https://github.com/dotnet/runtime/blob/master/LICENSE.TXT',
    'Microsoft.Bcl.Cryptography': 'https://github.com/dotnet/runtime/blob/master/LICENSE.TXT',
    'Microsoft.Build.Facade': 'https://github.com/dotnet/msbuild/blob/master/LICENSE',
    'Microsoft.Net.Http': 'https://github.com/dotnet/runtime/blob/master/LICENSE.TXT',
    'Microsoft.Win32.Primitives': 'https://github.com/dotnet/runtime/blob/master/LICENSE.TXT',
    'System.AppContext': 'https://github.com/dotnet/runtime/blob/master/LICENSE.TXT',
    'System.ClientModel': 'https://github.com/dotnet/runtime/blob/master/LICENSE.TXT',
    'System.CodeDom': 'https://github.com/dotnet/runtime/blob/master/LICENSE.TXT',
    'System.ComponentModel': 'https://github.com/dotnet/runtime/blob/master/LICENSE.TXT',
    'System.Console': 'https://github.com/dotnet/runtime/blob/master/LICENSE.TXT',
    'System.Data.DataSetExtensions': 'https://github.com/dotnet/runtime/blob/master/LICENSE.TXT',
    'System.Diagnostics.Tools': 'https://github.com/dotnet/runtime/blob/master/LICENSE.TXT',
    'System.Globalization.Calendars': 'https://github.com/dotnet/runtime/blob/master/LICENSE.TXT',
    'System.Globalization.Extensions': 'https://github.com/dotnet/runtime/blob/master/LICENSE.TXT',
    'System.IO.Compression.ZipFile': 'https://github.com/dotnet/runtime/blob/master/LICENSE.TXT',
    'System.Management': 'https://github.com/dotnet/runtime/blob/master/LICENSE.TXT',
    'System.Net.Http': 'https://github.com/dotnet/runtime/blob/master/LICENSE.TXT',
    'System.Net.Sockets': 'https://github.com/dotnet/runtime/blob/master/LICENSE.TXT',
    'System.Reflection.MetadataLoadContext': 'https://github.com/dotnet/runtime/blob/master/LICENSE.TXT',
    'System.Security.Cryptography.Csp': 'https://github.com/dotnet/runtime/blob/master/LICENSE.TXT',
    'System.Security.Cryptography.Pkcs': 'https://github.com/dotnet/runtime/blob/master/LICENSE.TXT',
    'System.Security.Cryptography.X509Certificates': 'https://github.com/dotnet/runtime/blob/master/LICENSE.TXT',
    'System.Security.Cryptography.Xml': 'https://github.com/dotnet/runtime/blob/master/LICENSE.TXT',
    'System.Text.RegularExpressions': 'https://github.com/dotnet/runtime/blob/master/LICENSE.TXT',
    'System.Threading.AccessControl': 'https://github.com/dotnet/runtime/blob/master/LICENSE.TXT',
    'System.Threading.Channels': 'https://github.com/dotnet/runtime/blob/master/LICENSE.TXT',
    'System.Threading.Tasks.DataFlow': 'https://github.com/dotnet/runtime/blob/master/LICENSE.TXT',
    'System.Threading.Timer': 'https://github.com/dotnet/runtime/blob/master/LICENSE.TXT',
    'System.Xml.ReaderWriter': 'https://github.com/dotnet/runtime/blob/master/LICENSE.TXT',
    'System.Xml.XDocument': 'https://github.com/dotnet/runtime/blob/master/LICENSE.TXT',
    
    # Microsoft Extensions (dotnet/runtime)
    'Microsoft.Data.Sqlite': 'https://github.com/dotnet/efcore/blob/master/LICENSE.txt',
    'Microsoft.Data.Sqlite.Core': 'https://github.com/dotnet/efcore/blob/master/LICENSE.txt',
    'Microsoft.Extensions.Caching.Abstractions': 'https://github.com/dotnet/runtime/blob/master/LICENSE.TXT',
    'Microsoft.Extensions.Caching.Memory': 'https://github.com/dotnet/runtime/blob/master/LICENSE.TXT',
    'Microsoft.Extensions.Configuration.CommandLine': 'https://github.com/dotnet/runtime/blob/master/LICENSE.TXT',
    'Microsoft.Extensions.Configuration.UserSecrets': 'https://github.com/dotnet/runtime/blob/master/LICENSE.TXT',
    'Microsoft.Extensions.DependencyModel': 'https://github.com/dotnet/runtime/blob/master/LICENSE.TXT',
    'Microsoft.Extensions.Diagnostics': 'https://github.com/dotnet/runtime/blob/master/LICENSE.TXT',
    'Microsoft.Extensions.Diagnostics.Abstractions': 'https://github.com/dotnet/runtime/blob/master/LICENSE.TXT',
    'Microsoft.Extensions.Hosting': 'https://github.com/dotnet/runtime/blob/master/LICENSE.TXT',
    'Microsoft.Extensions.Hosting.Abstractions': 'https://github.com/dotnet/runtime/blob/master/LICENSE.TXT',
    'Microsoft.Extensions.Logging.Debug': 'https://github.com/dotnet/runtime/blob/master/LICENSE.TXT',
    'Microsoft.Extensions.Logging.EventLog': 'https://github.com/dotnet/runtime/blob/master/LICENSE.TXT',
    'Microsoft.Extensions.Logging.EventSource': 'https://github.com/dotnet/runtime/blob/master/LICENSE.TXT',
    'Microsoft.FeatureManagement': 'https://github.com/microsoft/FeatureManagement-Dotnet/blob/main/LICENSE',
    
    # Microsoft Analyzers
    'Microsoft.CodeAnalysis.FxCopAnalyzers': 'https://github.com/dotnet/roslyn-analyzers/blob/master/License.txt',
    'Microsoft.CodeAnalysis.VersionCheckAnalyzer': 'https://github.com/dotnet/roslyn-analyzers/blob/master/License.txt',
    'Microsoft.CodeQuality.Analyzers': 'https://github.com/dotnet/roslyn-analyzers/blob/master/License.txt',
    'Microsoft.NetCore.Analyzers': 'https://github.com/dotnet/roslyn-analyzers/blob/master/License.txt',
    'Microsoft.NetFramework.Analyzers': 'https://github.com/dotnet/roslyn-analyzers/blob/master/License.txt',
    
    # Microsoft Visual Studio
    'Microsoft.VisualStudio.Setup.Configuration.Interop': 'https://www.nuget.org/packages/Microsoft.VisualStudio.Setup.Configuration.Interop/3.2.2146/License',
    
    # NETStandard
    'NETStandard.Library': 'https://github.com/dotnet/standard/blob/master/LICENSE.TXT',
    
    # Parquet
    'Parquet.Net': 'https://github.com/aloneguid/parquet-dotnet/blob/master/LICENSE',
    
    # Serilog
    'Serilog': 'https://github.com/serilog/serilog/blob/master/LICENSE',
    'Serilog.Extensions.Hosting': 'https://github.com/serilog/serilog-extensions-hosting/blob/master/LICENSE',
    'Serilog.Extensions.Logging': 'https://github.com/serilog/serilog-extensions-logging/blob/master/LICENSE',
    'Serilog.Formatting.Compact': 'https://github.com/serilog/serilog-formatting-compact/blob/master/LICENSE',
    'Serilog.Sinks.Debug': 'https://github.com/serilog/serilog-sinks-debug/blob/master/LICENSE',
    
    # Snappier
    'Snappier': 'https://github.com/brantburnett/Snappier/blob/master/LICENSE',
    
    # YamlDotNet
    'YamlDotNet': 'https://github.com/aaubry/YamlDotNet/blob/master/LICENSE.txt',
    
    # coverlet
    'coverlet.collector': 'https://github.com/coverlet-coverage/coverlet/blob/master/LICENSE',
    
    # log4net
    'log4net': 'https://github.com/apache/logging-log4net/blob/master/LICENSE',
    
    # runtime native packages
    'runtime.native.System.Net.Http': 'https://github.com/dotnet/runtime/blob/master/LICENSE.TXT',
    
    # xUnit
    'xunit': 'https://github.com/xunit/xunit/blob/master/LICENSE',
    'xunit.abstractions': 'https://github.com/xunit/xunit/blob/master/LICENSE',
    'xunit.assert': 'https://github.com/xunit/xunit/blob/master/LICENSE',
    'xunit.core': 'https://github.com/xunit/xunit/blob/master/LICENSE',
    'xunit.extensibility.core': 'https://github.com/xunit/xunit/blob/master/LICENSE',
    'xunit.extensibility.execution': 'https://github.com/xunit/xunit/blob/master/LICENSE',
    'xunit.runner.visualstudio': 'https://github.com/xunit/visualstudio.xunit/blob/master/License.txt',
    
    # NPM packages
    'playwright-trx-reporter': 'https://github.com/estruyf/playwright-trx-reporter/blob/master/LICENSE',
    'primereact': 'https://github.com/primefaces/primereact/blob/master/LICENSE.md',
    'react-intl': 'https://github.com/formatjs/formatjs/blob/master/LICENSE.md',
    
    # @formatjs packages
    '@formatjs/ecma402-abstract': 'https://github.com/formatjs/formatjs/blob/main/LICENSE.md',
    '@formatjs/intl': 'https://github.com/formatjs/formatjs/blob/main/LICENSE.md',
    'intl-messageformat': 'https://github.com/formatjs/formatjs/blob/main/LICENSE.md',
    
    # @inversifyjs packages
    '@inversifyjs/reflect-metadata-utils': 'https://github.com/inversify/monorepo/blob/main/LICENSE',
    
    # @isaacs packages
    '@isaacs/brace-expansion': 'https://github.com/isaacs/brace-expansion/blob/main/LICENSE',
    
    # @jridgewell packages
    '@jridgewell/gen-mapping': 'https://github.com/jridgewell/gen-mapping/blob/main/LICENSE',
    '@jridgewell/source-map': 'https://github.com/jridgewell/source-map/blob/main/LICENSE',
    '@jridgewell/sourcemap-codec': 'https://github.com/jridgewell/sourcemap-codec/blob/main/LICENSE',
    '@jridgewell/trace-mapping': 'https://github.com/jridgewell/trace-mapping/blob/main/LICENSE',
    
    # @swc packages
    '@swc/counter': 'https://github.com/swc-project/swc/blob/main/LICENSE',
    
    # Node.js packages
    'acorn-walk': 'https://github.com/acornjs/acorn/blob/master/acorn-walk/LICENSE',
    'cross-spawn': 'https://github.com/moxystudio/node-cross-spawn/blob/master/LICENSE',
    'dedent': 'https://github.com/dmnd/dedent/blob/master/LICENSE',
    'fast-uri': 'https://github.com/fastify/fast-uri/blob/main/LICENSE',
    'glob': 'https://github.com/isaacs/node-glob/blob/main/LICENSE.md',
    'minimatch': 'https://github.com/isaacs/minimatch/blob/main/LICENSE',
    'node-addon-api': 'https://github.com/nodejs/node-addon-api/blob/main/LICENSE.md',
    'object-inspect': 'https://github.com/inspect-js/object-inspect/blob/main/LICENSE',
    'parchment': 'https://github.com/quilljs/parchment/blob/main/LICENSE',
    'isbot': 'https://github.com/omrilotan/isbot/blob/main/LICENSE',
    'retry': 'https://github.com/tim-kos/node-retry/blob/master/License',
    'sql-highlight': 'https://github.com/scriptcoded/sql-highlight/blob/master/LICENSE',
    'typescript': 'https://github.com/microsoft/TypeScript/blob/main/LICENSE.txt',
    'undici-types': 'https://github.com/nodejs/undici/blob/main/LICENSE',
}
